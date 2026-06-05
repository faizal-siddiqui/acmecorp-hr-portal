from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

app = FastAPI(
    title="Salary Management API",
    description="HR salary management for ACME Corp — employee directory, compensation, analytics.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}
