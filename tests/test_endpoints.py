from unittest.mock import AsyncMock
import pytest

from app.schemas.company import InvoiceStatus
from app.services.database import DatabaseService

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_get_invoice_status_success(client):
    response = client.get("/api/invoice/1234567890123")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["corporate_number"] == "1234567890123"
    assert data["data"]["status"] == "registered"

def test_get_invoice_status_not_found(client):
    response = client.get("/api/invoice/1234567890000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_invoice_status_invalid_format(client):
    response = client.get("/api/invoice/12345")
    assert response.status_code == 400
    assert "13-digit" in response.json()["detail"]

def test_register_monitor_success(client):
    response = client.post(
        "/api/monitor/register",
        json={"corporate_number": "1234567890123", "webhook_url": "http://example.com/webhook"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "monitor_id" in data

def test_register_monitor_not_found(client):
    response = client.post(
        "/api/monitor/register",
        json={"corporate_number": "1234567890000", "webhook_url": "http://example.com/webhook"}
    )
    assert response.status_code == 404

def test_simulate_change_and_webhook(client, mocker):
    # Mock the asynchronous Webhook call to avoid actual requests and inspect call args
    mock_send = mocker.patch(
        "app.services.database.DatabaseService.send_webhook_notification",
        new_callable=AsyncMock
    )
    
    # 1. Register a monitor for corporate number 9876543210987
    webhook_url = "http://example.com/webhook-receiver"
    reg_response = client.post(
        "/api/monitor/register",
        json={"corporate_number": "9876543210987", "webhook_url": webhook_url}
    )
    assert reg_response.status_code == 200
    
    # 2. Simulate status change to cancelled
    sim_response = client.post(
        "/api/monitor/simulate-change",
        json={"corporate_number": "9876543210987", "new_status": "cancelled"}
    )
    assert sim_response.status_code == 200
    data = sim_response.json()
    assert data["success"] is True
    assert data["notifications_triggered"] == 1
    
    # 3. Verify mock send was called exactly once with correct parameters
    mock_send.assert_called_once()
    
    args, kwargs = mock_send.call_args
    passed_url = args[0]
    payload = args[1]
    
    assert passed_url == webhook_url
    assert payload.corporate_number == "9876543210987"
    assert payload.previous_status == InvoiceStatus.REGISTERED
    assert payload.current_status == InvoiceStatus.CANCELLED
