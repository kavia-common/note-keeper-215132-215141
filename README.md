# note-keeper-215132-215141

Backend (FastAPI) for Notes API.

How to run locally:
1) cd notes_backend
2) python -m venv .venv && source .venv/bin/activate
3) pip install -r requirements.txt
4) Optional: copy .env.example to .env and set DATABASE_URL
5) uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Environment:
- DATABASE_URL (defaults to sqlite:///./notes.db)

OpenAPI docs at /docs once running.