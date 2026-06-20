from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class InvoiceStatus(str, Enum):
    REGISTERED = "registered"  # 適格請求書発行事業者
    CANCELLED = "cancelled"    # 取消し
    EXPIRED = "expired"        # 失効（解散など）

class CompanyInfo(BaseModel):
    corporate_number: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$", description="13桁の法人番号")
    name: str = Field(..., description="事業者名")
    status: InvoiceStatus = Field(..., description="インボイス登録ステータス")
    registered_date: date = Field(..., description="登録年月日")
    update_date: date = Field(..., description="更新年月日")
    address: str = Field(..., description="本店又は主たる事務所の所在地")

class CompanyResponse(BaseModel):
    success: bool
    data: Optional[CompanyInfo] = None
    message: Optional[str] = None
