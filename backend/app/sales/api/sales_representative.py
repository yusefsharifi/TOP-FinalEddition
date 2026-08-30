from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.sales.services.sales_representative_service import SalesRepresentativeService
from app.sales.models.sales_representative import SalesRepStatus, SalesRepLevel
from app.utils.auth import get_current_user
from app.utils.schemas import Response

router = APIRouter()

@router.post("/sales-representatives/", response_model=Response)
async def create_sales_rep(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد فروشنده جدید"""
    service = SalesRepresentativeService(db)
    sales_rep = service.create_sales_rep(data)
    if not sales_rep:
        raise HTTPException(status_code=400, detail="خطا در ایجاد فروشنده")
    return Response(success=True, data=sales_rep)

@router.get("/sales-representatives/{sales_rep_id}", response_model=Response)
async def get_sales_rep(
    sales_rep_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت اطلاعات فروشنده"""
    service = SalesRepresentativeService(db)
    sales_rep = service.get_sales_rep(sales_rep_id)
    if not sales_rep:
        raise HTTPException(status_code=404, detail="فروشنده یافت نشد")
    return Response(success=True, data=sales_rep)

@router.put("/sales-representatives/{sales_rep_id}", response_model=Response)
async def update_sales_rep(
    sales_rep_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """به‌روزرسانی اطلاعات فروشنده"""
    service = SalesRepresentativeService(db)
    sales_rep = service.update_sales_rep(sales_rep_id, data)
    if not sales_rep:
        raise HTTPException(status_code=404, detail="فروشنده یافت نشد")
    return Response(success=True, data=sales_rep)

@router.post("/sales-regions/", response_model=Response)
async def create_region(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد منطقه فروش جدید"""
    service = SalesRepresentativeService(db)
    region = service.create_region(data)
    if not region:
        raise HTTPException(status_code=400, detail="خطا در ایجاد منطقه فروش")
    return Response(success=True, data=region)

@router.get("/sales-regions/{region_id}", response_model=Response)
async def get_region(
    region_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت اطلاعات منطقه فروش"""
    service = SalesRepresentativeService(db)
    region = service.get_region(region_id)
    if not region:
        raise HTTPException(status_code=404, detail="منطقه فروش یافت نشد")
    return Response(success=True, data=region)

@router.post("/sales-visits/", response_model=Response)
async def record_visit(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ثبت بازدید فروش"""
    service = SalesRepresentativeService(db)
    visit = service.record_visit(data)
    if not visit:
        raise HTTPException(status_code=400, detail="خطا در ثبت بازدید")
    return Response(success=True, data=visit)

@router.get("/sales-visits/", response_model=Response)
async def get_visits(
    sales_rep_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت لیست بازدیدهای فروشنده"""
    service = SalesRepresentativeService(db)
    visits = service.get_visits(sales_rep_id, start_date, end_date)
    return Response(success=True, data=visits)

@router.post("/sales-performance/", response_model=Response)
async def record_performance(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ثبت عملکرد فروش"""
    service = SalesRepresentativeService(db)
    performance = service.record_performance(data)
    if not performance:
        raise HTTPException(status_code=400, detail="خطا در ثبت عملکرد")
    return Response(success=True, data=performance)

@router.get("/sales-performance/{sales_rep_id}", response_model=Response)
async def get_performance(
    sales_rep_id: int,
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت عملکرد فروشنده"""
    service = SalesRepresentativeService(db)
    performance = service.get_performance(sales_rep_id, period_start, period_end)
    if not performance:
        raise HTTPException(status_code=404, detail="اطلاعات عملکرد یافت نشد")
    return Response(success=True, data=performance)

@router.get("/team-performance/{manager_id}", response_model=Response)
async def get_team_performance(
    manager_id: int,
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت عملکرد تیم فروش"""
    service = SalesRepresentativeService(db)
    team_performance = service.get_team_performance(manager_id, period_start, period_end)
    return Response(success=True, data=team_performance) 