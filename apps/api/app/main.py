from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import (
    auth_router,
    employees_router,
    analytics_router,
    export_router
)

app = FastAPI(
    title="Salary Management API",
    description="HR salary management for ACME Corp — employee directory, compensation, analytics.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    # Remove X-Powered-By and Server if present
    if "X-Powered-By" in response.headers:
        del response.headers["X-Powered-By"]
    if "Server" in response.headers:
        del response.headers["Server"]
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(analytics_router)
app.include_router(export_router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}
