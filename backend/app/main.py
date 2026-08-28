from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="NaCCER R&D Evaluation Copilot Backend",
    version=settings.VERSION,
    description="REST API service layer for NaCCER / CMPDI R&D Proposal Evaluation Platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Version 1 REST API Router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", summary="Root Health Endpoint")
def root_health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_PREFIX,
    }
