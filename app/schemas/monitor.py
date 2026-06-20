from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.schemas.company import InvoiceStatus, CompanyInfo

class MonitorRegisterRequest(BaseModel):
    corporate_number: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$", description="監視対象の13桁の法人番号")
    webhook_url: str = Field(..., description="ステータス変更時に通知を送信するWebhook URL")

class MonitorRegisterResponse(BaseModel):
    success: bool
    monitor_id: str
    message: str

class WebhookPayload(BaseModel):
    event_id: str = Field(..., description="イベントの一意なID")
    event_type: str = Field("invoice.status_changed", description="イベントタイプ (例: invoice.status_changed)")
    timestamp: datetime = Field(..., description="イベント発生日時")
    corporate_number: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$")
    previous_status: InvoiceStatus = Field(..., description="変更前のステータス")
    current_status: InvoiceStatus = Field(..., description="変更後のステータス")
    company_info: CompanyInfo = Field(..., description="最新の事業者情報")

class SimulateChangeRequest(BaseModel):
    corporate_number: str = Field(..., min_length=13, max_length=13, pattern=r"^\d{13}$", description="ステータスを変更する法人番号")
    new_status: InvoiceStatus = Field(..., description="新しいインボイス登録ステータス")

class SimulateChangeResponse(BaseModel):
    success: bool
    message: str
    notifications_triggered: int
