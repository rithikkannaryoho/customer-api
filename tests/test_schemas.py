from datetime import datetime

import pytest
from pydantic import ValidationError

from src.schemas import CustomerCreate, CustomerOut, CustomerUpdate


def test_create_rejects_bad_email():
    with pytest.raises(ValidationError):
        CustomerCreate(name="Arun", email="not-an-email")


def test_update_allows_partial_fields():
    update = CustomerUpdate(city="Chennai")
    assert update.model_dump(exclude_unset=True) == {"city": "Chennai"}


def test_out_reads_from_orm_object():
    from src.models import Customer

    obj = Customer(id=1, name="Arun", email="arun@example.com",
                   phone=None, city="Chennai", created_at=datetime(2026, 1, 1))
    assert CustomerOut.model_validate(obj).email == "arun@example.com"
