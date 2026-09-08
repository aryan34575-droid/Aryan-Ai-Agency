import os
from pathlib import Path
import yaml
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Aryan AI Agency", version="0.1.0")
AGENTS = yaml.safe_load(Path("agents.yaml").read_text())

class Task(BaseModel):
    message: str
    agent: str = "master"

def system_prompt(agent_key: str) -> str:
    agent = AGENTS.get(agent_key, AGENTS["master"])
    return f"""You are {agent['name']} in Aryan AI Agency.
Role: {agent['role']}

Work professionally and conservatively.
Do not invent facts, sources, credentials, actions, tool calls, or completed work.
State assumptions and uncertainty clearly.
When a task requires current information, say that live web research is required unless browsing tools are actually available.
Return useful, structured output with headings and actionable next steps.
"""

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "aryan-ai-agency"}

@app.get("/api/agents")
async def agents():
    return {k: v["name"] for k, v in AGENTS.items()}

@app.post("/api/task")
async def task(payload: Task):
    api_url = os.getenv("MODEL_API_URL", "").strip()
    api_key = os.getenv("MODEL_API_KEY", "").strip()
    model = os.getenv("MODEL_NAME", "").strip()

    if not api_url or not model:
        return {
            "status": "configuration_required",
            "message": "Add MODEL_API_URL and MODEL_NAME in Render Environment Variables.",
            "agent": payload.agent,
            "instructions": "The agency UI is live; connect an OpenAI-compatible model endpoint to enable AI responses."
        }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt(payload.agent)},
            {"role": "user", "content": payload.message},
        ],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(api_url.rstrip("/") + "/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
        content = data["choices"][0]["message"]["content"]
        return {"status": "ok", "agent": payload.agent, "answer": content}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Model provider error: {exc}")
