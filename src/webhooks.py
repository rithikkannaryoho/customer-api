import hashlib
import hmac
import json
import logging

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from src.config import WEBHOOK_SECRET

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger("uvicorn.error")      # shows up in the uvicorn console


def compute_signature(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def process_event(body: bytes):
    """Runs AFTER the 200 response has been sent."""
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        logger.warning("Webhook body is not valid JSON: %r", body[:100])
        return
    logger.info("Processed webhook event: type=%s data=%s",
                event.get("type"), event.get("data"))


@router.post("/customer-events")
async def customer_events(request: Request, background_tasks: BackgroundTasks,
                          x_signature: str | None = Header(default=None)):
    body = await request.body()                   # RAW bytes: the signature covers exactly these

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    expected = compute_signature(body)
    received = x_signature.removeprefix("sha256=")
    if not hmac.compare_digest(expected, received):      # constant-time comparison
        raise HTTPException(status_code=401, detail="Invalid signature")

    background_tasks.add_task(process_event, body)       # work happens after the response
    return {"status": "accepted"}