import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Invoice Status Monitor API"
    API_V1_STR: str = "/api"

    # When set, lock the origin to RapidAPI-proxied traffic (empty = open, for local/dev).
    RAPIDAPI_PROXY_SECRET: str = os.environ.get("RAPIDAPI_PROXY_SECRET", "")
    # Cap registered webhooks per company to bound memory.
    MAX_MONITORS_PER_COMPANY: int = 50
    
    # Rate limiting configurations
    RATE_LIMIT_INVOICE: str = "10/minute"
    RATE_LIMIT_MONITOR: str = "5/minute"
    
    # Webhook defaults
    WEBHOOK_TIMEOUT_SECONDS: int = 5

settings = Settings()
