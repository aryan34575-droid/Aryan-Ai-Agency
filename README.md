# Aryan AI Agency

A Render-friendly, free-first AI agency workspace for professional tasks.

## Included
- Master/CEO task router
- Research, Business, Data/Excel, Coding, Document and QA agents
- Simple browser dashboard
- OpenAI-compatible model API configuration
- Render deployment files

## Why this is not the full DeerFlow Compose stack
DeerFlow 2.0 is a multi-service system (frontend, gateway, Redis and optional sandbox/provisioner). Its official deployment guidance recommends more resources than a typical Render Free instance. This repository therefore provides a lightweight agency layer designed to deploy reliably on a single Render Web Service, with DeerFlow integration left as a later backend upgrade.

## Run locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

## Model configuration
Set these environment variables:
- MODEL_API_URL
- MODEL_API_KEY
- MODEL_NAME

The app expects an OpenAI-compatible `/chat/completions` endpoint.

Never commit API keys.

## Render
Create a Web Service from this GitHub repository:
- Runtime: Docker
- Instance: Free
- No paid plan required for this starter
- Add model secrets in Render Environment Variables

## Security
This starter is for personal/professional use. Before handling sensitive corporate data, add authentication, persistent storage, rate limiting, audit logs and isolated code execution.
