from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import DBDep, CurrentUser
from app.sales.services.subscription_service import SubscriptionService
from app.utils.schemas import Response

router = APIRouter()

@router.post("/subscriptions/", response_model=Response)
async def create_subscription(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد اشتراک جدید"""
    service = SubscriptionService(db)
    subscription = service.create_subscription(data)
    if not subscription:
        raise HTTPException(status_code=400, detail="خطا در ایجاد اشتراک")
    return Response(success=True, data=subscription)

@router.get("/subscriptions/{subscription_id}", response_model=Response)
async def get_subscription(
    subscription_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت اطلاعات اشتراک"""
    service = SubscriptionService(db)
    subscription = service.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="اشتراک یافت نشد")
    return Response(success=True, data=subscription)

@router.put("/subscriptions/{subscription_id}/status", response_model=Response)
async def update_subscription_status(
    subscription_id: int,
    status: str,
    db: DBDep,
    current_user: CurrentUser
):
    """به‌روزرسانی وضعیت اشتراک"""
    service = SubscriptionService(db)
    subscription = service.update_subscription_status(subscription_id, status)
    if not subscription:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی وضعیت اشتراک")
    return Response(success=True, data=subscription)

@router.post("/subscriptions/{subscription_id}/items/", response_model=Response)
async def add_subscription_item(
    subscription_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """افزودن آیتم به اشتراک"""
    service = SubscriptionService(db)
    item = service.add_subscription_item({**data, "subscription_id": subscription_id})
    if not item:
        raise HTTPException(status_code=400, detail="خطا در افزودن آیتم به اشتراک")
    return Response(success=True, data=item)

@router.post("/subscriptions/{subscription_id}/deliveries/", response_model=Response)
async def create_subscription_delivery(
    subscription_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد تحویل اشتراک"""
    service = SubscriptionService(db)
    delivery = service.create_subscription_delivery({**data, "subscription_id": subscription_id})
    if not delivery:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تحویل اشتراک")
    return Response(success=True, data=delivery)

@router.post("/subscriptions/{subscription_id}/deliveries/{delivery_id}/items/", response_model=Response)
async def add_delivery_item(
    subscription_id: int,
    delivery_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """افزودن آیتم به تحویل اشتراک"""
    service = SubscriptionService(db)
    delivery_item = service.add_delivery_item({**data, "delivery_id": delivery_id})
    if not delivery_item:
        raise HTTPException(status_code=400, detail="خطا در افزودن آیتم به تحویل اشتراک")
    return Response(success=True, data=delivery_item)

@router.post("/subscriptions/{subscription_id}/payments/", response_model=Response)
async def create_subscription_payment(
    subscription_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ثبت پرداخت اشتراک"""
    service = SubscriptionService(db)
    payment = service.create_subscription_payment({**data, "subscription_id": subscription_id})
    if not payment:
        raise HTTPException(status_code=400, detail="خطا در ثبت پرداخت اشتراک")
    return Response(success=True, data=payment)

@router.get("/subscriptions/{subscription_id}/totals", response_model=Response)
async def calculate_subscription_totals(
    subscription_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """محاسبه مجموع اشتراک"""
    service = SubscriptionService(db)
    totals = service.calculate_subscription_totals(subscription_id)
    if not totals:
        raise HTTPException(status_code=400, detail="خطا در محاسبه مجموع اشتراک")
    return Response(success=True, data=totals)

@router.get("/subscriptions/{subscription_id}/history", response_model=Response)
async def get_subscription_history(
    subscription_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تاریخچه اشتراک"""
    service = SubscriptionService(db)
    history = service.get_subscription_history(subscription_id)
    return Response(success=True, data=history)

@router.get("/customers/{customer_id}/subscriptions", response_model=Response)
async def get_customer_subscriptions(
    customer_id: int,
    status: Optional[str] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت اشتراک‌های مشتری"""
    service = SubscriptionService(db)
    subscriptions = service.get_customer_subscriptions(customer_id, status)
    return Response(success=True, data=subscriptions)

@router.get("/sales-reps/{sales_rep_id}/subscriptions", response_model=Response)
async def get_sales_rep_subscriptions(
    sales_rep_id: int,
    status: Optional[str] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت اشتراک‌های نماینده فروش"""
    service = SubscriptionService(db)
    subscriptions = service.get_sales_rep_subscriptions(sales_rep_id, status)
    return Response(success=True, data=subscriptions)

@router.get("/subscriptions/upcoming-deliveries", response_model=Response)
async def get_upcoming_deliveries(
    days: int = Query(7, description="تعداد روزهای پیش‌رو"),
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تحویل‌های پیش‌رو"""
    service = SubscriptionService(db)
    deliveries = service.get_upcoming_deliveries(days)
    return Response(success=True, data=deliveries)

@router.post("/subscriptions/deliveries/{delivery_id}/process", response_model=Response)
async def process_subscription_delivery(
    delivery_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """پردازش تحویل اشتراک"""
    service = SubscriptionService(db)
    delivery = service.process_subscription_delivery(delivery_id)
    if not delivery:
        raise HTTPException(status_code=400, detail="خطا در پردازش تحویل اشتراک")
    return Response(success=True, data=delivery) 