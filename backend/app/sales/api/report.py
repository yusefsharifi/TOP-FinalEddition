from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.sales.services.report_service import ReportService
from app.utils.auth import get_current_user
from app.utils.schemas import Response

router = APIRouter()

@router.post("/reports/", response_model=Response)
async def create_report(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد گزارش جدید"""
    service = ReportService(db)
    report = service.create_report({**data, "created_by": current_user.id})
    if not report:
        raise HTTPException(status_code=400, detail="خطا در ایجاد گزارش")
    return Response(success=True, data=report)

@router.get("/reports/{report_id}", response_model=Response)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت اطلاعات گزارش"""
    service = ReportService(db)
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="گزارش یافت نشد")
    return Response(success=True, data=report)

@router.put("/reports/{report_id}/status", response_model=Response)
async def update_report_status(
    report_id: int,
    status: str,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """به‌روزرسانی وضعیت گزارش"""
    service = ReportService(db)
    report = service.update_report_status(report_id, status, error_message)
    if not report:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی وضعیت گزارش")
    return Response(success=True, data=report)

@router.post("/reports/{report_id}/data/", response_model=Response)
async def add_report_data(
    report_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """افزودن داده به گزارش"""
    service = ReportService(db)
    report_data = service.add_report_data({**data, "report_id": report_id})
    if not report_data:
        raise HTTPException(status_code=400, detail="خطا در افزودن داده به گزارش")
    return Response(success=True, data=report_data)

@router.post("/report-templates/", response_model=Response)
async def create_report_template(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد قالب گزارش"""
    service = ReportService(db)
    template = service.create_report_template({**data, "created_by": current_user.id})
    if not template:
        raise HTTPException(status_code=400, detail="خطا در ایجاد قالب گزارش")
    return Response(success=True, data=template)

@router.get("/report-templates/{template_id}", response_model=Response)
async def get_report_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت قالب گزارش"""
    service = ReportService(db)
    template = service.get_report_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="قالب گزارش یافت نشد")
    return Response(success=True, data=template)

@router.post("/report-schedules/", response_model=Response)
async def create_report_schedule(
    data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """ایجاد زمانبندی گزارش"""
    service = ReportService(db)
    schedule = service.create_report_schedule(data)
    if not schedule:
        raise HTTPException(status_code=400, detail="خطا در ایجاد زمانبندی گزارش")
    return Response(success=True, data=schedule)

@router.get("/report-schedules/{schedule_id}", response_model=Response)
async def get_report_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت زمانبندی گزارش"""
    service = ReportService(db)
    schedule = service.get_report_schedule(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="زمانبندی گزارش یافت نشد")
    return Response(success=True, data=schedule)

@router.get("/users/{user_id}/reports", response_model=Response)
async def get_user_reports(
    user_id: int,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت گزارش‌های کاربر"""
    service = ReportService(db)
    reports = service.get_user_reports(user_id, report_type)
    return Response(success=True, data=reports)

@router.get("/report-templates/public", response_model=Response)
async def get_public_templates(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت قالب‌های عمومی"""
    service = ReportService(db)
    templates = service.get_public_templates()
    return Response(success=True, data=templates)

@router.get("/reports/scheduled", response_model=Response)
async def get_scheduled_reports(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """دریافت گزارش‌های زمانبندی شده"""
    service = ReportService(db)
    reports = service.get_scheduled_reports()
    return Response(success=True, data=reports)

@router.get("/reports/sales-summary", response_model=Response)
async def generate_sales_summary(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش خلاصه فروش"""
    service = ReportService(db)
    data = service.generate_sales_summary(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/product-performance", response_model=Response)
async def generate_product_performance(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش عملکرد محصولات"""
    service = ReportService(db)
    data = service.generate_product_performance(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/customer-analysis", response_model=Response)
async def generate_customer_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش تحلیل مشتریان"""
    service = ReportService(db)
    data = service.generate_customer_analysis(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/sales-rep-performance", response_model=Response)
async def generate_sales_rep_performance(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش عملکرد نمایندگان فروش"""
    service = ReportService(db)
    data = service.generate_sales_rep_performance(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/regional-analysis", response_model=Response)
async def generate_regional_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش تحلیل منطقه‌ای"""
    service = ReportService(db)
    data = service.generate_regional_analysis(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/trend-analysis", response_model=Response)
async def generate_trend_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش تحلیل روند"""
    service = ReportService(db)
    data = service.generate_trend_analysis(start_date, end_date)
    return Response(success=True, data=data)

@router.get("/reports/inventory-analysis", response_model=Response)
async def generate_inventory_analysis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """تولید گزارش تحلیل موجودی"""
    service = ReportService(db)
    data = service.generate_inventory_analysis()
    return Response(success=True, data=data) 