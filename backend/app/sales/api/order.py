from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.sales.services.order_service import OrderService
from app.utils.auth import get_current_user
from app.utils.schemas import Response

router = APIRouter()

@router.post("/orders/", response_model=Response)
async def create_order(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد سفارش جدید"""
    service = OrderService(db)
    order = service.create_order(data)
    if not order:
        raise HTTPException(status_code=400, detail="خطا در ایجاد سفارش")
    return Response(success=True, data=order)

@router.get("/orders/{order_id}", response_model=Response)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت اطلاعات سفارش"""
    service = OrderService(db)
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")
    return Response(success=True, data=order)

@router.put("/orders/{order_id}/status", response_model=Response)
async def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """به‌روزرسانی وضعیت سفارش"""
    service = OrderService(db)
    order = service.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی وضعیت سفارش")
    return Response(success=True, data=order)

@router.post("/orders/{order_id}/items/", response_model=Response)
async def add_order_item(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن آیتم به سفارش"""
    service = OrderService(db)
    item = service.add_order_item({**data, "order_id": order_id})
    if not item:
        raise HTTPException(status_code=400, detail="خطا در افزودن آیتم به سفارش")
    return Response(success=True, data=item)

@router.post("/orders/{order_id}/payments/", response_model=Response)
async def create_order_payment(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ثبت پرداخت سفارش"""
    service = OrderService(db)
    payment = service.create_order_payment({**data, "order_id": order_id})
    if not payment:
        raise HTTPException(status_code=400, detail="خطا در ثبت پرداخت سفارش")
    return Response(success=True, data=payment)

@router.post("/orders/{order_id}/shipments/", response_model=Response)
async def create_order_shipment(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ثبت ارسال سفارش"""
    service = OrderService(db)
    shipment = service.create_order_shipment({**data, "order_id": order_id})
    if not shipment:
        raise HTTPException(status_code=400, detail="خطا در ثبت ارسال سفارش")
    return Response(success=True, data=shipment)

@router.post("/orders/{order_id}/returns/", response_model=Response)
async def create_order_return(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ثبت مرجوعی سفارش"""
    service = OrderService(db)
    order_return = service.create_order_return({**data, "order_id": order_id})
    if not order_return:
        raise HTTPException(status_code=400, detail="خطا در ثبت مرجوعی سفارش")
    return Response(success=True, data=order_return)

@router.post("/orders/{order_id}/returns/{return_id}/items/", response_model=Response)
async def add_return_item(
    order_id: int,
    return_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن آیتم به مرجوعی"""
    service = OrderService(db)
    return_item = service.add_return_item({**data, "order_return_id": return_id})
    if not return_item:
        raise HTTPException(status_code=400, detail="خطا در افزودن آیتم به مرجوعی")
    return Response(success=True, data=return_item)

@router.get("/orders/{order_id}/totals", response_model=Response)
async def calculate_order_totals(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """محاسبه مجموع سفارش"""
    service = OrderService(db)
    totals = service.calculate_order_totals(order_id)
    if not totals:
        raise HTTPException(status_code=400, detail="خطا در محاسبه مجموع سفارش")
    return Response(success=True, data=totals)

@router.get("/orders/{order_id}/history", response_model=Response)
async def get_order_history(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت تاریخچه سفارش"""
    service = OrderService(db)
    history = service.get_order_history(order_id)
    return Response(success=True, data=history)

@router.get("/customers/{customer_id}/orders", response_model=Response)
async def get_customer_orders(
    customer_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت سفارشات مشتری"""
    service = OrderService(db)
    orders = service.get_customer_orders(customer_id, status)
    return Response(success=True, data=orders)

@router.get("/sales-reps/{sales_rep_id}/orders", response_model=Response)
async def get_sales_rep_orders(
    sales_rep_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت سفارشات نماینده فروش"""
    service = OrderService(db)
    orders = service.get_sales_rep_orders(sales_rep_id, status)
    return Response(success=True, data=orders) 