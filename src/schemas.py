from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)


class CustomerUpdate(BaseModel):
    """Every field is optional so PUT/PATCH can change just one."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None
    city: str | None
    created_at: datetime


class CustomerPage(BaseModel):
    page: int
    per_page: int
    total: int
    items: list[CustomerOut]