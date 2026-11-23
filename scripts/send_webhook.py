"""Signs a payload with the secret from .env and posts it: valid, tampered, missing signature."""
import hashlib
import hmac
import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))

URL = "http://127.0.0.1:8000/webhooks/customer-events"
SECRET = os.environ["WEBHOOK_SECRET"].encode()


def sign(body: bytes) -> str:
    return hmac.new(SECRET, body, hashlib.sha256).hexdigest()


original = json.dumps({"type": "customer.created", "data": {"id": 1, "name": "Arun"}}).encode()
tampered = json.dumps({"type": "customer.created", "data": {"id": 1, "name": "Hacker"}}).encode()

r = httpx.post(URL, content=original, headers={"X-Signature": sign(original)})
print("Valid signature ->", r.status_code, r.text)

r = httpx.post(URL, content=tampered, headers={"X-Signature": sign(original)})   # signed the original, sent changed body
print("Tampered payload ->", r.status_code, r.text)

r = httpx.post(URL, content=original)
print("Missing signature ->", r.status_code, r.text)