from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, SessionLocal, Base, get_db, db, ensure_columns
from .models import Project, Event, Issue, ConflictTicket, SMSLog, FieldSubmission
from .services.seeder import seed_data
from .routers import (
    auth_router,
    projects_router,
    issues_router,
    conflicts_router,
    onsite_router,
    geocode_router,
    broadcasts_router
)

# Initialize FastAPI Application
app = FastAPI(
    title='Utopia API',
    version='3.0.0',
    description='Smart Public Works Transparency & Municipal Operations Platform'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include Modular Routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(issues_router)
app.include_router(conflicts_router)
app.include_router(onsite_router)
app.include_router(geocode_router)
app.include_router(broadcasts_router)

@app.on_event("startup")
def on_startup():
    # Create all tables if not exist
    Base.metadata.create_all(bind=engine)
    # Ensure any dynamic columns exist on SQLite or Postgres
    ensure_columns(engine)
    # Seed initial demo data
    with SessionLocal() as s:
        seed_data(s)

@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Utopia Smart Municipal Operations Platform",
        "version": "3.0.0"
    }

@app.get("/", tags=["Health"])
def root_status():
    return {
        "message": "Welcome to Utopia — Municipal Operations & Public Works API",
        "docs": "/docs",
        "health": "/api/health"
    }
