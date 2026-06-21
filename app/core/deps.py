from fastapi import Header, HTTPException, Request
from slowapi import Limiter

from app.core.config import settings


def client_ip(request: Request) -> str:
    """Real client IP for rate limiting. Behind Render's proxy, request.client.host is
    the proxy, so prefer the first hop in X-Forwarded-For."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "anonymous"


limiter = Limiter(key_func=client_ip)


async def require_proxy_secret(x_rapidapi_proxy_secret: str = Header(None)):
    """When RAPIDAPI_PROXY_SECRET is set, only allow RapidAPI-proxied requests (locks the
    origin). When unset (local/dev), requests pass through."""
    secret = settings.RAPIDAPI_PROXY_SECRET
    if secret and x_rapidapi_proxy_secret != secret:
        raise HTTPException(status_code=403,
                            detail="Requests must go through the RapidAPI marketplace.")
