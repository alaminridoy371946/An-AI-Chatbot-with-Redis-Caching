AI Chatbot with Redis Caching & GitHub Models
A production-ready, async, cached AI chatbot powered by GitHub Models (OpenAI-compatible) using FastAPI + Redis.

Features

Real LLM responses via GitHub Models (gpt-4.1-nano, gpt-4o-mini, etc.)
Redis caching (10-minute TTL) → 90%+ faster repeated queries
Async + retry logic (3 attempts with exponential backoff)
Secure config via .env (no hardcoded secrets)
OpenAPI docs at /docs
Health check, cache stats, cache clear
Docker + Docker Compose ready



LayerTechWeb FrameworkFastAPIAI InferenceOpenAI SDK (Async)CacheRedisConfigpython-dotenvContainerDocker

Project Structure
text.
├── ai_engine.py      → LLM inference with retry
├── cache.py          → Redis cache wrapper
├── main.py           → FastAPI app & routes
├── .env              → Your secrets (gitignored)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

Setup (2 Minutes)
1. Clone & Enter
bashgit clone <your-repo>
cd <repo>
2. Create .env
envBASE_URL="https://models.inference.ai.azure.com"
API_KEY="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"
MODEL_NAME="gpt-4.1-nano"

Use gpt-4o-mini for faster/cheaper responses.

3. Run with Docker (Recommended)
bashdocker compose up --build
API: http://localhost:8000
Docs: http://localhost:8000/docs


































MethodEndpointDescriptionGET/API infoGET/healthCheck Redis + APIPOST/chatAsk AI (cached)GET/cache/statsRedis statsDELETE/cache/clearClear all cache

Example: Ask AI
bashcurl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain FastAPI in 2 sentences"}'
First call (cached: false):
Second call (cached: true): ~5ms!

Clear Cache (If Stuck with Old Error)
bashcurl -X DELETE http://localhost:8000/cache/clear

Local Development (No Docker)
bashpip install -r requirements.txt
uvicorn main:app --reload

requirements.txt
txtfastapi
uvicorn[standard]
openai>=1.30.0
redis
python-dotenv

GitHub Models Notes

Endpoint: https://models.inference.ai.azure.com
Auth: GitHub PAT with read:packages
Models: gpt-4.1-nano, gpt-4o-mini, meta-llama/Meta-Llama-3.1-8B-Instruct, etc.
Docs: https://github.com/marketplace/models


Troubleshooting





















IssueFix401 Invalid API keyUse correct BASE_URL + valid PATCached errorRun /cache/clearModel not foundRemove openai/ prefix → use gpt-4.1-nano

Production Tips

Use Docker secrets for API_KEY
Add rate limiting (slowapi)
Enable Prometheus metrics
Add JWT auth for /cache/clear