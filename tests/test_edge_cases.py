from fastapi.testclient import TestClient

from src.database import get_db
from src.main import app
from src.webhooks import compute_signature

client = TestClient(app)
AUTH = {"X-API-Key": "test-key"}
WEBHOOK = "/webhooks/customer-events"


class BrokenDB:
    def execute(self, *args, **kwargs):
        raise RuntimeError("database is down")


def test_health_returns_503_when_database_is_down():
    app.dependency_overrides[get_db] = lambda: BrokenDB()
    try:
        r = client.get("/health")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 503


def test_list_empty_database_returns_empty_page():
    r = client.get("/customers", headers=AUTH)
    assert r.status_code == 200
    assert r.json() == {"page": 1, "per_page": 10, "total": 0, "items": []}


def test_invalid_pagination_returns_422():
    assert client.get("/customers?page=0", headers=AUTH).status_code == 422
    assert client.get("/customers?per_page=101", headers=AUTH).status_code == 422


def test_webhook_accepts_sha256_prefix():
    body = b'{"type": "customer.updated", "data": {"id": 2}}'
    r = client.post(WEBHOOK, content=body,
                    headers={"X-Signature": "sha256=" + compute_signature(body)})
    assert r.status_code == 200


def test_webhook_with_valid_signature_but_invalid_json_is_still_accepted():
    body = b"this is not json"
    r = client.post(WEBHOOK, content=body, headers={"X-Signature": compute_signature(body)})
    assert r.status_code == 200
