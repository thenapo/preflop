
# Preflop Advisor API

Wraps your range book into a simple API.
Built with **FastAPI**.

## Endpoints
- `POST /recommend` – Open/Shove recommendation for unopened pots.
- `POST /vs-open` – 3-bet advice versus an opener (Value/Bluff/Shove).
- `GET /docs` – Swagger UI.
- `GET /health` – health check.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs

### Examples (HTTP)

```bash
# Open/Shove (auto):
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"hand":"AJo","position":"MP","stack":40,"context":"auto"}'

# 3-bet vs open:
curl -X POST http://127.0.0.1:8000/vs-open \
  -H "Content-Type: application/json" \
  -d '{"hand":"QQ","hero_pos":"SB","opener_pos":"MP","stack":50}'
```

## Deploy on Render

1. Push this folder to GitHub.
2. In Render, create a **Web Service** connected to the repo.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Region: nearest to you.

That's it. Visit `/docs` on the Render URL.
