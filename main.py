import os
from pathlib import Path
import httpx
import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

with open(BASE_DIR / "agents.yaml", "r", encoding="utf-8") as f:
    AGENTS = yaml.safe_load(f)["agents"]

app = FastAPI(title="Aryan AI Agency")

class TaskRequest(BaseModel):
    message: str
    agent: str = "master"

@app.get("/")
async def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "aryan-ai-agency"}

@app.get("/api/agents")
async def agents():
    return AGENTS

@app.post("/api/task")
async def task(req: TaskRequest):
    url = os.getenv("MODEL_API_URL")
    key = os.getenv("MODEL_API_KEY")
    model = os.getenv("MODEL_NAME")

    if not url or not key or not model:
        return {"status":"configuration_required",
                "message":"Add MODEL_API_URL, MODEL_API_KEY and MODEL_NAME in Render Environment Variables."}

    agent = AGENTS.get(req.agent, AGENTS["master"])
    payload = {
        "model": model,
        "messages": [
            {"role":"system","content":agent.get("system_prompt","You are a helpful AI assistant.")},
            {"role":"user","content":req.message}
        ],
        "temperature": 0.2
    }
    headers = {"Authorization":f"Bearer {key}","Content-Type":"application/json"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url.rstrip("/") + "/chat/completions",
                                  headers=headers, json=payload)
        data = r.json()
        if r.status_code >= 400:
            return {"status":"model_error","http_status":r.status_code,"error":data}
        return {"status":"success","agent":req.agent,"model":data.get("model",model),
                "result":data["choices"][0]["message"]["content"]}
    except Exception as e:
        return {"status":"request_error","error":str(e)}
