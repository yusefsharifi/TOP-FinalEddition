from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.sales.services.customer_service import CustomerService
from app.utils.auth import get_current_user
from app.utils.schemas import Response

router = APIRouter()

@router.post("/customers/", response_model=Response)
async def create_customer(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد مشتری جدید"""
    service = CustomerService(db)
    customer = service.create_customer({**data, "created_by": current_user.id})
    if not customer:
        raise HTTPException(status_code=400, detail="خطا در ایجاد مشتری")
    return Response(success=True, data=customer)

@router.get("/customers/{customer_id}", response_model=Response)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت اطلاعات مشتری"""
    service = CustomerService(db)
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="مشتری یافت نشد")
    return Response(success=True, data=customer)

@router.put("/customers/{customer_id}", response_model=Response)
async def update_customer(
    customer_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """به‌روزرسانی اطلاعات مشتری"""
    service = CustomerService(db)
    customer = service.update_customer(customer_id, data)
    if not customer:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی مشتری")
    return Response(success=True, data=customer)

@router.put("/customers/{customer_id}/status", response_model=Response)
async def update_customer_status(
    customer_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """به‌روزرسانی وضعیت مشتری"""
    service = CustomerService(db)
    customer = service.update_customer_status(customer_id, status)
    if not customer:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی وضعیت مشتری")
    return Response(success=True, data=customer)

@router.post("/customers/{customer_id}/contacts/", response_model=Response)
async def add_customer_contact(
    customer_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن مخاطب به مشتری"""
    service = CustomerService(db)
    contact = service.add_customer_contact({**data, "customer_id": customer_id})
    if not contact:
        raise HTTPException(status_code=400, detail="خطا در افزودن مخاطب")
    return Response(success=True, data=contact)

@router.get("/customers/{customer_id}/contacts/", response_model=Response)
async def get_customer_contacts(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت مخاطبین مشتری"""
    service = CustomerService(db)
    contacts = service.get_customer_contacts(customer_id)
    return Response(success=True, data=contacts)

@router.post("/customers/{customer_id}/notes/", response_model=Response)
async def add_customer_note(
    customer_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن یادداشت به مشتری"""
    service = CustomerService(db)
    note = service.add_customer_note({**data, "customer_id": customer_id, "created_by": current_user.id})
    if not note:
        raise HTTPException(status_code=400, detail="خطا در افزودن یادداشت")
    return Response(success=True, data=note)

@router.get("/customers/{customer_id}/notes/", response_model=Response)
async def get_customer_notes(
    customer_id: int,
    note_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت یادداشت‌های مشتری"""
    service = CustomerService(db)
    notes = service.get_customer_notes(customer_id, note_type)
    return Response(success=True, data=notes)

@router.post("/customers/{customer_id}/activities/", response_model=Response)
async def add_customer_activity(
    customer_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن فعالیت به مشتری"""
    service = CustomerService(db)
    activity = service.add_customer_activity({**data, "customer_id": customer_id, "created_by": current_user.id})
    if not activity:
        raise HTTPException(status_code=400, detail="خطا در افزودن فعالیت")
    return Response(success=True, data=activity)

@router.get("/customers/{customer_id}/activities/", response_model=Response)
async def get_customer_activities(
    customer_id: int,
    activity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت فعالیت‌های مشتری"""
    service = CustomerService(db)
    activities = service.get_customer_activities(customer_id, activity_type)
    return Response(success=True, data=activities)

@router.post("/customer-segments/", response_model=Response)
async def create_customer_segment(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد بخش مشتریان"""
    service = CustomerService(db)
    segment = service.create_customer_segment({**data, "created_by": current_user.id})
    if not segment:
        raise HTTPException(status_code=400, detail="خطا در ایجاد بخش مشتریان")
    return Response(success=True, data=segment)

@router.get("/customer-segments/{segment_id}", response_model=Response)
async def get_customer_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت بخش مشتریان"""
    service = CustomerService(db)
    segment = service.get_customer_segment(segment_id)
    if not segment:
        raise HTTPException(status_code=404, detail="بخش مشتریان یافت نشد")
    return Response(success=True, data=segment)

@router.get("/customer-segments/{segment_id}/customers/", response_model=Response)
async def get_customers_by_segment(
    segment_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت مشتریان یک بخش"""
    service = CustomerService(db)
    customers = service.get_customers_by_segment(segment_id)
    return Response(success=True, data=customers)

@router.get("/customers/search/", response_model=Response)
async def search_customers(
    query: str,
    customer_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """جستجوی مشتریان"""
    service = CustomerService(db)
    customers = service.search_customers(query, customer_type)
    return Response(success=True, data=customers)

@router.get("/sales-reps/{sales_rep_id}/customers/", response_model=Response)
async def get_customers_by_sales_rep(
    sales_rep_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت مشتریان نماینده فروش"""
    service = CustomerService(db)
    customers = service.get_customers_by_sales_rep(sales_rep_id, status)
    return Response(success=True, data=customers)

@router.get("/territories/{territory}/customers/", response_model=Response)
async def get_customers_by_territory(
    territory: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت مشتریان یک منطقه"""
    service = CustomerService(db)
    customers = service.get_customers_by_territory(territory, status)
    return Response(success=True, data=customers)

@router.get("/customers/{customer_id}/statistics/", response_model=Response)
async def get_customer_statistics(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت آمار مشتری"""
    service = CustomerService(db)
    statistics = service.get_customer_statistics(customer_id)
    return Response(success=True, data=statistics) 