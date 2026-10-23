from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from app.config import settings, logger
from app.database import init_db
from app.modules.lead_routing.router import router as leads_router
from app.adapters.airtable_adapter import airtable_adapter
from app.adapters.slack_adapter import slack_adapter
from app.adapters.email_adapter import email_adapter
from app.adapters.sheets_adapter import sheets_adapter
from app.adapters.stripe_adapter import stripe_adapter
from app.adapters.openai_adapter import openai_adapter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed default knowledge base
    init_db()
    logger.info("Application startup: database ready, adapters initialized.")
    yield
    # Shutdown
    logger.info("Application shutdown.")

app = FastAPI(
    title=settings.app_name,
    description="Enterprise AI Automation Suite with Lead Intelligence, Support Triage, Invoice Scanner, and Multi-Agent Ops.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(leads_router, prefix="/api/v1")

@app.get("/api/v1/health", tags=["System"])
def health_check():
    """System health check and adapter connectivity status."""
    return {
        "status": "HEALTHY",
        "demo_mode": settings.demo_mode,
        "environment": settings.app_env,
        "adapters": {
            "airtable": airtable_adapter.health_check(),
            "slack": slack_adapter.health_check(),
            "email": email_adapter.health_check(),
            "sheets": sheets_adapter.health_check(),
            "stripe": stripe_adapter.health_check(),
            "openai": openai_adapter.health_check()
        }
    }
