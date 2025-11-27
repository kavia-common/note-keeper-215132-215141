from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers_notes import router as notes_router

openapi_tags = [
    {"name": "Health", "description": "Service health endpoints"},
    {"name": "Notes", "description": "CRUD operations for notes"},
]

app = FastAPI(
    title="Notes API",
    description="A simple Notes service with CRUD functionality.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS: Allow local frontend at port 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def on_startup():
    init_db()


# PUBLIC_INTERFACE
@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Simple health check endpoint to verify the service is running.",
)
def health_check():
    """Returns a simple JSON to indicate service health."""
    return {"message": "Healthy"}

# Include Notes router
app.include_router(notes_router)
