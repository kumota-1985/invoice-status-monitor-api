from fastapi import APIRouter, Request, HTTPException, status

from app.schemas.company import CompanyResponse
from app.services.database import DatabaseService
from app.core.deps import limiter
from app.core.config import settings

router = APIRouter()

@router.get("/invoice/{corporate_number}", response_model=CompanyResponse)
@limiter.limit(settings.RATE_LIMIT_INVOICE)
def get_invoice_status(request: Request, corporate_number: str):
    """
    Look up qualified invoice issuer status by corporate number.
    Rate limited to prevent abuse.
    """
    # Simple check for corporate number pattern (13-digit string)
    if not (corporate_number.isdigit() and len(corporate_number) == 13):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corporate number must be a 13-digit number."
        )
    
    company = DatabaseService.get_company(corporate_number)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with corporate number {corporate_number} not found in database."
        )
    
    return CompanyResponse(success=True, data=company)
