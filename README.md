# note-keeper-215132-215141

Backend (FastAPI) for Notes API.

How to run locally:
1) cd notes_backend
2) python -m venv .venv && source .venv/bin/activate
3) pip install -r requirements.txt
4) Create .env and set DATABASE_URL to your Supabase Postgres URI (required)
5) uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Environment:
- DATABASE_URL (required; Supabase Postgres URI like postgresql+psycopg2://...:5432/postgres?sslmode=require)
- Optional: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY (not required for direct SQLAlchemy access)

OpenAPI docs at /docs once running.

Supabase Configuration Required
1. In Supabase Dashboard:
   - Create the project and retrieve Database connection string, SUPABASE_URL and keys.
   - Authentication > URL Configuration: set Site URL and add redirects for http://localhost:3000/** and your production domain.
2. Backend connection:
   - Use DATABASE_URL pointing to Supabase Postgres (postgresql+psycopg2://...&sslmode=require).
3. Schema:
   - Table public.notes with UUID id, title, content, tags jsonb, is_archived, created_at, updated_at.
   - RLS enabled; authenticated full CRUD for development.

Notes:
- The backend now uses UUID primary keys and exposes them as strings in the API.
- Field "archived" in the API maps to the database column "is_archived".
- Tags are supported via a string array exposed as `tags` (stored as jsonb).

For a sample .env.example, set:
DATABASE_URL=postgresql+psycopg2://postgres:<PASSWORD>@<HOST>:5432/postgres?sslmode=require