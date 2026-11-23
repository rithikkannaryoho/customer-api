from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Customer
from src.schemas import CustomerCreate, CustomerOut, CustomerPage, CustomerUpdate
from src.security import verify_api_key

# one dependency protects every route in this router
router = APIRouter(prefix="/customers", tags=["customers"],
                   dependencies=[Depends(verify_api_key)])


def get_or_404(db: Session, customer_id: int) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(**data.model_dump())
    db.add(customer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    db.refresh(customer)
    return customer


@router.get("", response_model=CustomerPage)
def list_customers(page: int = Query(1, ge=1),
                   per_page: int = Query(10, ge=1, le=100),
                   db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Customer))
    items = db.scalars(
        select(Customer).order_by(Customer.id)
        .offset((page - 1) * per_page).limit(per_page)
    ).all()
    return {"page": page, "per_page": per_page, "total": total, "items": items}


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = get_or_404(db, customer_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = get_or_404(db, customer_id)
    db.delete(customer)
    db.commit()