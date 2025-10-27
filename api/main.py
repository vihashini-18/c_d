from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from api.routes import chat, audio, health
from api.middleware.error_handler import setup_error_handlers
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Medical Chatbot API...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Using CUDA: {settings.USE_CUDA}")
    
    # Initialize services here if needed
    # await initialize_services()
    
    yield
    
    # Shutdown
    print("Shutting down Medical Chatbot API...")
    # Cleanup code here

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Medical Chatbot API",
        description="Advanced medical chatbot with multimodal RAG capabilities",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.DEBUG else ["yourdomain.com", "*.yourdomain.com"]
    )
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    app.include_router(audio.router, prefix="/api/v1", tags=["audio"])
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Medical Chatbot API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs" if settings.DEBUG else "disabled"
        }
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
