from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.config import settings
from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.db.session import engine, Base
from app.middleware.error_handler import ErrorHandlingMiddleware, PerformanceMiddleware
from app.services.session_manager import SessionManager
from app.monitoring.metrics import metrics_collector, RequestMetrics
from app.utils.logger import Logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    app_logger = Logger().get_logger("app")
    app_logger.info("Starting Customer Bot application")
    
    # Create database tables
    os.makedirs("data", exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Lightweight migration for existing SQLite DBs (adds new columns if missing)
        try:
            result = await conn.execute(text("PRAGMA table_info('chat_sessions')"))
            existing_cols = {row[1] for row in result.fetchall()}  

            
            if "expires_at" not in existing_cols:
                await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN expires_at DATETIME"))
            if "is_active" not in existing_cols:
                await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
            if "message_count" not in existing_cols:
                await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN message_count INTEGER DEFAULT 0 NOT NULL"))
            if "last_activity" not in existing_cols:
                await conn.execute(text("ALTER TABLE chat_sessions ADD COLUMN last_activity DATETIME"))
        except Exception as mig_err:
            app_logger.warning(f"Startup migration check failed: {mig_err}")
    
   
    #  Session cleanup will be handled by the SessionManager when used
    app_logger.info("Background tasks initialized")
    
    app_logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    app_logger.info("Shutting down Customer Bot application")
    # Cleanup tasks will be handled automatically by the SessionManager
    app_logger.info("Application shutdown complete")


app = FastAPI(
    title="AI Customer Support Bot",
    version="2.0.0",
    description="""
    Advanced AI-powered customer support bot with RAG capabilities, session management, and comprehensive monitoring.
    
    ## Features
    
    * **Intelligent Responses**: Uses RAG (Retrieval-Augmented Generation) with vector embeddings
    * **Session Management**: Persistent conversation sessions with automatic cleanup
    * **Multi-tier Responses**: FAQ-based → General knowledge → Human escalation
    * **Conversation Summarization**: Automatic summaries of long conversations
    * **Action Suggestions**: Contextual next-step recommendations
    * **Performance Monitoring**: Comprehensive metrics and logging
    * **Error Handling**: Robust error handling with structured logging
    
    ## API Endpoints
    
    * `/api/chat` - Main chat endpoint with enhanced features
    * `/api/summarize` - Generate conversation summaries
    * `/api/suggest-actions` - Get contextual action suggestions
    * `/api/ingest/faq` - Ingest FAQ data into the knowledge base
    * `/api/health` - Health check endpoint
    * `/api/metrics` - Performance metrics endpoint
    * `/api/sessions/stats` - Session statistics endpoint
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/metrics")
async def get_metrics():
    """Get system performance metrics."""
    system_metrics = await metrics_collector.get_system_metrics()
    endpoint_metrics = await metrics_collector.get_endpoint_metrics()
    
    return {
        "system_metrics": system_metrics.__dict__,
        "endpoint_metrics": endpoint_metrics,
        "timestamp": system_metrics.timestamp.isoformat()
    }

@app.get("/api/sessions/stats")
async def get_session_stats():
    """Get session statistics."""
    # This would need to be implemented with proper DB session by the SessionManager
    return {
        "message": "Session stats endpoint - requires DB session implementation",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Include routers
app.include_router(ingest_router, prefix="/api/ingest", tags=["ingest"]) 
app.include_router(chat_router, prefix="/api", tags=["chat"]) 
