from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.deps import DBDep, CurrentUser
from app.sales.services.product_service import ProductService
from app.utils.schemas import Response

router = APIRouter()

@router.post("/products/", response_model=Response)
async def create_product(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد محصول جدید"""
    service = ProductService(db)
    product = service.create_product({**data, "created_by": current_user.id})
    if not product:
        raise HTTPException(status_code=400, detail="خطا در ایجاد محصول")
    return Response(success=True, data=product)

@router.get("/products/{product_id}", response_model=Response)
async def get_product(
    product_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت اطلاعات محصول"""
    service = ProductService(db)
    product = service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="محصول یافت نشد")
    return Response(success=True, data=product)

@router.put("/products/{product_id}", response_model=Response)
async def update_product(
    product_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """به‌روزرسانی اطلاعات محصول"""
    service = ProductService(db)
    product = service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی محصول")
    return Response(success=True, data=product)

@router.put("/products/{product_id}/status", response_model=Response)
async def update_product_status(
    product_id: int,
    status: str,
    db: DBDep,
    current_user: CurrentUser
):
    """به‌روزرسانی وضعیت محصول"""
    service = ProductService(db)
    product = service.update_product_status(product_id, status)
    if not product:
        raise HTTPException(status_code=400, detail="خطا در به‌روزرسانی وضعیت محصول")
    return Response(success=True, data=product)

@router.post("/product-categories/", response_model=Response)
async def create_product_category(
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد دسته‌بندی محصول"""
    service = ProductService(db)
    category = service.create_product_category(data)
    if not category:
        raise HTTPException(status_code=400, detail="خطا در ایجاد دسته‌بندی محصول")
    return Response(success=True, data=category)

@router.get("/product-categories/{category_id}", response_model=Response)
async def get_product_category(
    category_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت دسته‌بندی محصول"""
    service = ProductService(db)
    category = service.get_product_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="دسته‌بندی محصول یافت نشد")
    return Response(success=True, data=category)

@router.post("/products/{product_id}/variants/", response_model=Response)
async def create_product_variant(
    product_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد تنوع محصول"""
    service = ProductService(db)
    variant = service.create_product_variant({**data, "product_id": product_id})
    if not variant:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تنوع محصول")
    return Response(success=True, data=variant)

@router.get("/products/{product_id}/variants/{variant_id}", response_model=Response)
async def get_product_variant(
    product_id: int,
    variant_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تنوع محصول"""
    service = ProductService(db)
    variant = service.get_product_variant(variant_id)
    if not variant or variant.product_id != product_id:
        raise HTTPException(status_code=404, detail="تنوع محصول یافت نشد")
    return Response(success=True, data=variant)

@router.post("/products/{product_id}/prices/", response_model=Response)
async def create_product_price(
    product_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد قیمت محصول"""
    service = ProductService(db)
    price = service.create_product_price({**data, "product_id": product_id})
    if not price:
        raise HTTPException(status_code=400, detail="خطا در ایجاد قیمت محصول")
    return Response(success=True, data=price)

@router.get("/products/{product_id}/prices/", response_model=Response)
async def get_product_prices(
    product_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت قیمت‌های محصول"""
    service = ProductService(db)
    prices = service.get_product_prices(product_id)
    return Response(success=True, data=prices)

@router.post("/products/{product_id}/reviews/", response_model=Response)
async def create_product_review(
    product_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد نظر محصول"""
    service = ProductService(db)
    review = service.create_product_review({**data, "product_id": product_id})
    if not review:
        raise HTTPException(status_code=400, detail="خطا در ایجاد نظر محصول")
    return Response(success=True, data=review)

@router.get("/products/{product_id}/reviews/", response_model=Response)
async def get_product_reviews(
    product_id: int,
    approved_only: bool = True,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت نظرات محصول"""
    service = ProductService(db)
    reviews = service.get_product_reviews(product_id, approved_only)
    return Response(success=True, data=reviews)

@router.post("/products/{product_id}/images/", response_model=Response)
async def create_product_image(
    product_id: int,
    data: dict,
    db: DBDep,
    current_user: CurrentUser
):
    """ایجاد تصویر محصول"""
    service = ProductService(db)
    image = service.create_product_image({**data, "product_id": product_id})
    if not image:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تصویر محصول")
    return Response(success=True, data=image)

@router.get("/products/{product_id}/images/", response_model=Response)
async def get_product_images(
    product_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت تصاویر محصول"""
    service = ProductService(db)
    images = service.get_product_images(product_id)
    return Response(success=True, data=images)

@router.get("/products/search/", response_model=Response)
async def search_products(
    query: str,
    category_id: Optional[int] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """جستجوی محصولات"""
    service = ProductService(db)
    products = service.search_products(query, category_id)
    return Response(success=True, data=products)

@router.get("/product-categories/{category_id}/products/", response_model=Response)
async def get_products_by_category(
    category_id: int,
    status: Optional[str] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت محصولات یک دسته‌بندی"""
    service = ProductService(db)
    products = service.get_products_by_category(category_id, status)
    return Response(success=True, data=products)

@router.get("/sales-reps/{sales_rep_id}/products/", response_model=Response)
async def get_products_by_sales_rep(
    sales_rep_id: int,
    status: Optional[str] = None,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت محصولات نماینده فروش"""
    service = ProductService(db)
    products = service.get_products_by_sales_rep(sales_rep_id, status)
    return Response(success=True, data=products)

@router.get("/products/{product_id}/statistics/", response_model=Response)
async def get_product_statistics(
    product_id: int,
    db: DBDep,
    current_user: CurrentUser
):
    """دریافت آمار محصول"""
    service = ProductService(db)
    statistics = service.get_product_statistics(product_id)
    return Response(success=True, data=statistics) 