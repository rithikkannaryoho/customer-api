import os

# Separate TEST database + test secrets: set before the app is imported
os.environ["DATABASE_URL"] = "sqlite:///./test_customers.db"
os.environ["API_KEY"] = "test-key"
os.environ["WEBHOOK_SECRET"] = "test-secret"

import pytest

from src.database import Base, engine
import src.models  # noqa: F401  (registers the Customer table)


@pytest.fixture(autouse=True)
def fresh_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
