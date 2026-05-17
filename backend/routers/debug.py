from fastapi import APIRouter
from tasks.email_tasks import send_alert_email

router = APIRouter(prefix="/api/debug", tags=["debug"])

@router.post("/send-test-email")
def test_email(to: str, subject: str = "Test", body: str = "Test email"):
    # fire and forget — don't wait for result
    send_alert_email.delay(to, subject, body)
    return {"status": "queued"}