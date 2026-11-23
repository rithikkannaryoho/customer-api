from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
AUTH = {"X-API-Key": "test-key"}


def make(name="Arun", email="arun@example.com", **extra):
    return client.post("/customers", json={"name": name, "email": email, **extra}, headers=AUTH)


def test_create_returns_201():
    r = make(phone="9999999999", city="Chennai")
    print(f"\nPOST /customers -> {r.status_code}")
    assert r.status_code == 201
    assert r.json()["email"] == "arun@example.com" and "created_at" in r.json()


def test_list_with_pagination_returns_200():
    for i in range(12):
        make(name=f"User{i}", email=f"u{i}@example.com")
    r = client.get("/customers?page=1&per_page=10", headers=AUTH)
    print(f"\nGET /customers?page=1&per_page=10 -> {r.status_code}")
    assert r.status_code == 200
    body = r.json()
    assert len(body["items"]) == 10 and body["total"] == 12
    assert len(client.get("/customers?page=2&per_page=10", headers=AUTH).json()["items"]) == 2


def test_get_one_customer():
    cid = make().json()["id"]
    assert client.get(f"/customers/{cid}", headers=AUTH).status_code == 200


def test_unknown_id_returns_404():
    r = client.get("/customers/999", headers=AUTH)
    print(f"\nGET /customers/999 -> {r.status_code}")
    assert r.status_code == 404


def test_duplicate_email_returns_409():
    assert make().status_code == 201
    assert make(name="Other").status_code == 409


def test_update_customer_and_update_conflict():
    first = make().json()["id"]
    make(name="Priya", email="priya@example.com")
    r = client.put(f"/customers/{first}", json={"city": "Mumbai"}, headers=AUTH)
    assert r.status_code == 200 and r.json()["city"] == "Mumbai"
    assert client.put(f"/customers/{first}", json={"email": "priya@example.com"}, headers=AUTH).status_code == 409
    assert client.put("/customers/999", json={"city": "X"}, headers=AUTH).status_code == 404


def test_delete_customer():
    cid = make().json()["id"]
    assert client.delete(f"/customers/{cid}", headers=AUTH).status_code == 204
    assert client.get(f"/customers/{cid}", headers=AUTH).status_code == 404
    assert client.delete(f"/customers/{cid}", headers=AUTH).status_code == 404


def test_missing_api_key_returns_401():
    r = client.get("/customers")
    print(f"\nNo API key -> {r.status_code}")
    assert r.status_code == 401


def test_wrong_api_key_returns_403():
    assert client.get("/customers", headers={"X-API-Key": "wrong"}).status_code == 403


def test_invalid_body_returns_422():
    assert make(email="not-an-email").status_code == 422
