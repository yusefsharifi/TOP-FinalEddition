from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import DBDep, CurrentUser
from app.sales.services.pricing_service import PricingService
from app.utils.schemas import Response

router = APIRouter()

@router.post("/pricing-rules/", response_model=Response)
async def create_pricing_rule(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد قانون قیمت‌گذاری جدید"""
    service = PricingService(db)
    rule = service.create_pricing_rule(data)
    if not rule:
        raise HTTPException(status_code=400, detail="خطا در ایجاد قانون قیمت‌گذاری")
    return Response(success=True, data=rule)

@router.get("/pricing-rules/{rule_id}", response_model=Response)
async def get_pricing_rule(
    rule_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت اطلاعات قانون قیمت‌گذاری"""
    service = PricingService(db)
    rule = service.get_pricing_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="قانون قیمت‌گذاری یافت نشد")
    return Response(success=True, data=rule)

@router.post("/price-adjustments/", response_model=Response)
async def create_price_adjustment(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد تنظیم قیمت جدید"""
    service = PricingService(db)
    adjustment = service.create_price_adjustment(data)
    if not adjustment:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تنظیم قیمت")
    return Response(success=True, data=adjustment)

@router.get("/price-adjustments/{rule_id}", response_model=Response)
async def get_price_adjustments(
    rule_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تنظیمات قیمت یک قانون"""
    service = PricingService(db)
    adjustments = service.get_price_adjustments(rule_id)
    return Response(success=True, data=adjustments)

@router.post("/dynamic-pricing/", response_model=Response)
async def create_dynamic_pricing(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد قیمت‌گذاری پویا جدید"""
    service = PricingService(db)
    dynamic_pricing = service.create_dynamic_pricing(data)
    if not dynamic_pricing:
        raise HTTPException(status_code=400, detail="خطا در ایجاد قیمت‌گذاری پویا")
    return Response(success=True, data=dynamic_pricing)

@router.post("/dynamic-pricing/{dynamic_pricing_id}/update-price", response_model=Response)
async def update_dynamic_price(
    dynamic_pricing_id: int,
    new_price: float,
    reason: str,
    db: DBDep,
    current_user: CurrentUser
):
    """به‌روزرسانی قیمت پویا"""
    service = PricingService(db)
    price_history = service.update_dynamic_price(dynamic_pricing_id, new_price, reason)
    if not price_history:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی قیمت")
    return Response(success=True, data=price_history)

@router.get("/dynamic-pricing/{dynamic_pricing_id}/history", response_model=Response)
async def get_price_history(
    dynamic_pricing_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تاریخچه قیمت"""
    service = PricingService(db)
    history = service.get_price_history(dynamic_pricing_id, start_date, end_date)
    return Response(success=True, data=history)

@router.post("/volume-discounts/", response_model=Response)
async def create_volume_discount(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد تخفیف حجمی جدید"""
    service = PricingService(db)
    discount = service.create_volume_discount(data)
    if not discount:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تخفیف حجمی")
    return Response(success=True, data=discount)

@router.get("/calculate-price/", response_model=Response)
async def calculate_final_price(
    product_id: int = Query(...),
    quantity: int = Query(...),
    customer_segment_id: Optional[int] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """محاسبه قیمت نهایی"""
    service = PricingService(db)
    final_price = service.calculate_final_price(product_id, quantity, customer_segment_id)
    return Response(success=True, data={"final_price": final_price})

@router.get("/active-discounts/", response_model=Response)
async def get_active_discounts(
    product_id: int = Query(...),
    quantity: int = Query(...),
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تخفیف‌های فعال"""
    service = PricingService(db)
    discounts = service.get_active_discounts(product_id, quantity)
    return Response(success=True, data=discounts) 