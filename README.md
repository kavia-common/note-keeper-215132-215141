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
- Optional Supabase: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

OpenAPI docs at /docs once running.

Supabase Configuration Required
1. In Supabase Dashboard:
   - Create the project and retrieve Database connection string, SUPABASE_URL and keys.
   - Authentication > URL Configuration: set Site URL and add redirects for http://localhost:3000/** and your production domain.
2. Backend connection options:
   - Prefer DATABASE_URL pointing to Supabase Postgres (postgresql+psycopg2://...&sslmode=require).
   - Alternatively, integrate supabase-py for PostgREST access.
3. Schema:
   - Table public.notes with UUID id, title, content, tags jsonb, is_archived, created_at, updated_at.
   - RLS enabled; authenticated full CRUD for development.
4. Migration:
   - Current models use integer id and archived; update models/schemas to UUID + is_archived + tags to fully align, or map fields when calling Supabase.