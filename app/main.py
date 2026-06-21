import hashlib
from contextlib import asynccontextmanager

# Python 3.8.3 compatibility patch: hashlib.md5 does not support 'usedforsecurity' parameter
try:
    hashlib.md5(usedforsecurity=False)
except TypeError:
    original_md5 = hashlib.md5
    def md5_patched(*args, **kwargs):
        kwargs.pop('usedforsecurity', None)
        return original_md5(*args, **kwargs)
    hashlib.md5 = md5_patched

import httpx
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.deps import limiter, require_proxy_secret
from app.routers import r01_invoice_api, r02_monitor_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the shared HTTPX client for non-blocking outbound requests
    app.state.client = httpx.AsyncClient()
    yield
    # Shutdown: Properly clean up the client sessions
    await app.state.client.aclose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sandbox/demo API: qualified-invoice-issuer status lookup + webhook monitoring. "
                "Company data is a small built-in MOCK set (3 companies), NOT the live "
                "National Tax Agency registry. For demonstration and integration testing.",
    lifespan=lifespan
)

# Attach rate limiter to app state and register the handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # public API uses header keys, not cookies; "*"+credentials is invalid
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration (gated by the RapidAPI proxy secret when configured)
app.include_router(r01_invoice_api.router, prefix=settings.API_V1_STR, tags=["Invoice"],
                   dependencies=[Depends(require_proxy_secret)])
app.include_router(r02_monitor_api.router, prefix=settings.API_V1_STR, tags=["Monitor"],
                   dependencies=[Depends(require_proxy_secret)])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Invoice Status Monitor API",
        "docs": f"{settings.API_V1_STR}/docs" if not app.root_path else "/docs"
    }
