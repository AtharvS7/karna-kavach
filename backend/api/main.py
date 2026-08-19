"""
FastAPI backend main application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
from typing import AsyncGenerator

from api.routes import attacks, generate, predict
from db.database import engine, Base
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager - startup and shutdown events."""
    # Startup
    logger.info("Starting Karna Kavach API...")

    # Create database tables (if Postgres is available)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.warning(f"Database connection skipped ({e}) — running in fallback mode with JSON data")

    logger.info("API server ready")

    yield

    # Shutdown
    logger.info("Shutting down Karna Kavach API...")
    await engine.dispose()
    logger.info("Cleanup complete")


# Initialize FastAPI app
app = FastAPI(
    title="Karna Kavach API",
    description="AI Defense Lab for Payment Security - Red Team/Blue Team Fraud Detection System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Karna Kavach API - AI Defense Lab for Payment Security",
        "status": "operational",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "karna-kavach-api"
        }
    )


# Include routers
app.include_router(attacks.router, prefix="/api/attacks", tags=["Attacks"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generate"])
app.include_router(predict.router, prefix="/api/predict", tags=["Predict"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
