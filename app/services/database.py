import uuid
from datetime import date, datetime
from typing import Dict, List, Optional
import httpx

from app.schemas.company import CompanyInfo, InvoiceStatus
from app.schemas.monitor import WebhookPayload
from app.core.config import settings

# Mock National Tax Agency Invoice Database (Japanese Corporate Numbers are 13 digits)
MOCK_INVOICE_DB: Dict[str, dict] = {
    "1234567890123": {
        "corporate_number": "1234567890123",
        "name": "株式会社テストテクノロジー",
        "status": InvoiceStatus.REGISTERED,
        "registered_date": date(2023, 10, 1),
        "update_date": date(2023, 10, 1),
        "address": "東京都千代田区麹町1-1",
    },
    "9876543210987": {
        "corporate_number": "9876543210987",
        "name": "サンプル商事合同会社",
        "status": InvoiceStatus.REGISTERED,
        "registered_date": date(2023, 10, 1),
        "update_date": date(2023, 10, 1),
        "address": "大阪府大阪市中央区本町2-2",
    },
    "1111111111111": {
        "corporate_number": "1111111111111",
        "name": "鈴木デジタル商店",
        "status": InvoiceStatus.CANCELLED,
        "registered_date": date(2023, 10, 1),
        "update_date": date(2024, 5, 10),
        "address": "愛知県名古屋市中区栄3-3",
    }
}

# Monitoring list structure: { corporate_number: [ { "monitor_id": str, "webhook_url": str } ] }
MONITOR_DB: Dict[str, List[dict]] = {}

class DatabaseService:
    @staticmethod
    def get_company(corporate_number: str) -> Optional[CompanyInfo]:
        """Retrieve company info by corporate number."""
        data = MOCK_INVOICE_DB.get(corporate_number)
        if data:
            return CompanyInfo(**data)
        return None

    @staticmethod
    def register_monitor(corporate_number: str, webhook_url: str) -> str:
        """Register a Webhook URL for a specific corporate number."""
        if corporate_number not in MONITOR_DB:
            MONITOR_DB[corporate_number] = []
        
        monitor_id = str(uuid.uuid4())
        MONITOR_DB[corporate_number].append({
            "monitor_id": monitor_id,
            "webhook_url": webhook_url
        })
        return monitor_id

    @staticmethod
    def get_monitors(corporate_number: str) -> List[dict]:
        """Retrieve all registered monitors for a corporate number."""
        return MONITOR_DB.get(corporate_number, [])

    @staticmethod
    def update_company_status(corporate_number: str, new_status: InvoiceStatus) -> Optional[CompanyInfo]:
        """Update company status and update_date. Returns updated CompanyInfo or None."""
        if corporate_number in MOCK_INVOICE_DB:
            MOCK_INVOICE_DB[corporate_number]["status"] = new_status
            MOCK_INVOICE_DB[corporate_number]["update_date"] = date.today()
            return CompanyInfo(**MOCK_INVOICE_DB[corporate_number])
        return None

    @staticmethod
    async def send_webhook_notification(webhook_url: str, payload: WebhookPayload, client: httpx.AsyncClient) -> bool:
        """Sends the Webhook event asynchronously using a shared httpx client."""
        try:
            # model_dump(mode="json") converts datetime and enum objects to JSON-serializable types
            json_data = payload.model_dump(mode="json")
            response = await client.post(
                webhook_url,
                json=json_data,
                timeout=settings.WEBHOOK_TIMEOUT_SECONDS
            )
            # Standard successful POST requests return 2xx status codes
            return 200 <= response.status_code < 300
        except Exception as e:
            print(f"Failed to send webhook to {webhook_url}: {e}")
            return False
