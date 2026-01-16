"""
AI Financial Planning Agent - Main Application
FastAPI backend with multi-agent system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import budget, goals, health, chat
from app.utils.config import settings
from app.services.llm_service import LLMService
from app.services.vector_service import VectorService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    logger.info("Starting AI Financial Planning Agent...")
    
    # Initialize services
    try:
        # Initialize LLM service
        llm_service = LLMService()
        app.state.llm_service = llm_service
        logger.info(f"LLM Service initialized with provider: {settings.LLM_PROVIDER}")
        
        # Initialize vector service
        vector_service = VectorService()
        app.state.vector_service = vector_service
        logger.info("Vector Service initialized")
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Financial Planning Agent...")


# Create FastAPI app
app = FastAPI(
    title="AI Financial Planning Agent",
    description="Zero-cost AI-powered financial planning assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "service": "AI Financial Planning Agent",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "llm": settings.LLM_PROVIDER,
            "vector_db": "operational",
            "database": "operational"
        }
    }


# Include routers
app.include_router(budget.router, prefix="/api/budget", tags=["Budget"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(health.router, prefix="/api/health-score", tags=["Health Score"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
