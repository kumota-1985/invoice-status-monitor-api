import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks

from app.schemas.monitor import (
    MonitorRegisterRequest,
    MonitorRegisterResponse,
    SimulateChangeRequest,
    SimulateChangeResponse,
    WebhookPayload
)
from app.services.database import DatabaseService
from app.core.deps import limiter
from app.core.config import settings

router = APIRouter()

@router.post("/monitor/register", response_model=MonitorRegisterResponse)
@limiter.limit(settings.RATE_LIMIT_MONITOR)
def register_monitor(request: Request, body: MonitorRegisterRequest):
    """
    Register a Webhook URL to monitor status changes for a specific corporate number.
    """
    # Check if the company exists in the simulated database
    company = DatabaseService.get_company(body.corporate_number)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with corporate number {body.corporate_number} not found."
        )
    
    monitor_id = DatabaseService.register_monitor(body.corporate_number, body.webhook_url)
    return MonitorRegisterResponse(
        success=True,
        monitor_id=monitor_id,
        message=f"Successfully registered monitor for {body.corporate_number}."
    )

@router.post("/monitor/simulate-change", response_model=SimulateChangeResponse)
def simulate_change(request: Request, body: SimulateChangeRequest, background_tasks: BackgroundTasks):
    """
    Simulate a status change of a company to test webhook notifications.
    Triggers Webhook notifications in the background to all registered listeners.
    """
    # Get current company info
    company_before = DatabaseService.get_company(body.corporate_number)
    if not company_before:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with corporate number {body.corporate_number} not found."
        )
    
    previous_status = company_before.status
    if previous_status == body.new_status:
        return SimulateChangeResponse(
            success=True,
            message="No status change detected. Webhook notification skipped.",
            notifications_triggered=0
        )
    
    # Update status in the database
    company_after = DatabaseService.update_company_status(body.corporate_number, body.new_status)
    
    # Fetch all registered monitors
    monitors = DatabaseService.get_monitors(body.corporate_number)
    
    # Retrieve the shared HTTPX client from application state
    client = request.app.state.client
    
    triggered_count = 0
    for monitor in monitors:
        # Construct the webhook payload
        payload = WebhookPayload(
            event_id=str(uuid.uuid4()),
            event_type="invoice.status_changed",
            timestamp=datetime.now(timezone.utc),
            corporate_number=body.corporate_number,
            previous_status=previous_status,
            current_status=body.new_status,
            company_info=company_after
        )
        
        # Enqueue the webhook request as a background task
        background_tasks.add_task(
            DatabaseService.send_webhook_notification,
            monitor["webhook_url"],
            payload,
            client
        )
        triggered_count += 1
        
    return SimulateChangeResponse(
        success=True,
        message=f"Status successfully updated from '{previous_status.value}' to '{body.new_status.value}'.",
        notifications_triggered=triggered_count
    )
