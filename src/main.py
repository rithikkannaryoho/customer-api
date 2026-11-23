from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.customers import router as customers_router
from src.database import get_db
from src.webhooks import router as webhooks_router

app = FastAPI(title="Customer API", version="0.3.0")
app.include_router(customers_router)
app.include_router(webhooks_router)     # secured by HMAC signature instead of the API key


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Open endpoint for monitoring: liveness + database check."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "database": "up"}