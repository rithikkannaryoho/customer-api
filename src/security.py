import hmac

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from src.config import API_KEY

# auto_error=False so we return our own 401/403; this also adds the Authorize button in /docs
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)):
    """Reusable dependency: 401 if the key is missing, 403 if it is wrong."""
    if api_key is None:
        raise HTTPException(status_code=401, detail="API key missing")
    if not hmac.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API key")