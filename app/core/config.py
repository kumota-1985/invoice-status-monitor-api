import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Invoice Status Monitor API"
    API_V1_STR: str = "/api"
    
    # Rate limiting configurations
    RATE_LIMIT_INVOICE: str = "10/minute"
    RATE_LIMIT_MONITOR: str = "5/minute"
    
    # Webhook defaults
    WEBHOOK_TIMEOUT_SECONDS: int = 5

settings = Settings()
