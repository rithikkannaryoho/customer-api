import json
import logging

from fastapi.testclient import TestClient

from src.main import app
from src.webhooks import compute_signature

client = TestClient(app)
URL = "/webhooks/customer-events"


def payload(event_type="customer.created") -> bytes:
    return json.dumps({"type": event_type, "data": {"id": 1}}).encode()


def test_valid_signature_returns_200_and_accepted():
    body = payload()
    r = client.post(URL, content=body, headers={"X-Signature": compute_signature(body)})
    print(f"\nValid signature -> {r.status_code} {r.json()}")
    assert r.status_code == 200
    assert r.json() == {"status": "accepted"}


def test_tampered_payload_returns_401():
    signature = compute_signature(payload())
    tampered = payload("customer.deleted")            # changed after signing
    r = client.post(URL, content=tampered, headers={"X-Signature": signature})
    print(f"\nTampered payload -> {r.status_code} {r.json()}")
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid signature"}


def test_missing_signature_returns_401():
    r = client.post(URL, content=payload())
    print(f"\nMissing signature -> {r.status_code}")
    assert r.status_code == 401


def test_event_is_processed_in_background(caplog):
    body = payload()
    with caplog.at_level(logging.INFO, logger="uvicorn.error"):
        client.post(URL, content=body, headers={"X-Signature": compute_signature(body)})
    assert "Processed webhook event: type=customer.created" in caplog.text
