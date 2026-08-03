import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.config.settings import settings
from backend.app.database.session import init_db
from backend.app.api.router import api_router
from backend.app.middleware.cors import setup_cors
from backend.app.middleware.logging_middleware import LoggingMiddleware
from backend.app.middleware.rate_limit import RateLimitMiddleware
from backend.app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database tables...")
    await init_db()
    logger.info("OmniAgent AI system online and ready (Ollama + ChromaDB).")
    yield
    logger.info("Shutting down OmniAgent AI...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Zero-Cost Local Multi-Agent AI Platform using LangGraph, Ollama, ChromaDB, and Free LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup Middlewares
setup_cors(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120)

# Include API Router
app.include_router(api_router)

# Mount Static Frontend
frontend_path = settings.BASE_DIR / "frontend"
if frontend_path.exists():
    out_dir = frontend_path / "out"
    static_dir = out_dir if out_dir.exists() else frontend_path
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    css_dir = static_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")

    js_dir = static_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    @app.get("/")
    async def serve_index():
        if (static_dir / "index.html").exists():
            return FileResponse(str(static_dir / "index.html"))
        return {"message": "OmniAgent AI API Server is running. Access API docs at /docs"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER,
        "vectorstore": "ChromaDB"
    }

from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal Server Error"}
    )
