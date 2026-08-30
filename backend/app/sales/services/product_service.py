from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.sales.models.product import (
    Product, ProductCategory, ProductVariant,
    ProductPrice, ProductReview, ProductImage,
    ProductType, ProductStatus
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, data: Dict[str, Any]) -> Optional[Product]:
        """ایجاد محصول جدید"""
        try:
            product = Product(**data)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            self.db.rollback()
            return None

    def get_product(self, product_id: int) -> Optional[Product]:
        """دریافت اطلاعات محصول"""
        try:
            return self.db.query(Product).filter(
                Product.id == product_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting product: {str(e)}")
            return None

    def update_product(self, product_id: int, data: Dict[str, Any]) -> Optional[Product]:
        """به‌روزرسانی اطلاعات محصول"""
        try:
            product = self.get_product(product_id)
            if not product:
                return None

            for key, value in data.items():
                setattr(product, key, value)

            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            self.db.rollback()
            return None

    def update_product_status(self, product_id: int, status: str) -> Optional[Product]:
        """به‌روزرسانی وضعیت محصول"""
        try:
            product = self.get_product(product_id)
            if not product:
                return None

            product.status = status
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            logger.error(f"Error updating product status: {str(e)}")
            self.db.rollback()
            return None

    def create_product_category(self, data: Dict[str, Any]) -> Optional[ProductCategory]:
        """ایجاد دسته‌بندی محصول"""
        try:
            category = ProductCategory(**data)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            logger.error(f"Error creating product category: {str(e)}")
            self.db.rollback()
            return None

    def get_product_category(self, category_id: int) -> Optional[ProductCategory]:
        """دریافت دسته‌بندی محصول"""
        try:
            return self.db.query(ProductCategory).filter(
                ProductCategory.id == category_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting product category: {str(e)}")
            return None

    def create_product_variant(self, data: Dict[str, Any]) -> Optional[ProductVariant]:
        """ایجاد تنوع محصول"""
        try:
            variant = ProductVariant(**data)
            self.db.add(variant)
            self.db.commit()
            self.db.refresh(variant)
            return variant
        except Exception as e:
            logger.error(f"Error creating product variant: {str(e)}")
            self.db.rollback()
            return None

    def get_product_variant(self, variant_id: int) -> Optional[ProductVariant]:
        """دریافت تنوع محصول"""
        try:
            return self.db.query(ProductVariant).filter(
                ProductVariant.id == variant_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting product variant: {str(e)}")
            return None

    def create_product_price(self, data: Dict[str, Any]) -> Optional[ProductPrice]:
        """ایجاد قیمت محصول"""
        try:
            price = ProductPrice(**data)
            self.db.add(price)
            self.db.commit()
            self.db.refresh(price)
            return price
        except Exception as e:
            logger.error(f"Error creating product price: {str(e)}")
            self.db.rollback()
            return None

    def get_product_prices(self, product_id: int) -> List[ProductPrice]:
        """دریافت قیمت‌های محصول"""
        try:
            return self.db.query(ProductPrice).filter(
                ProductPrice.product_id == product_id,
                ProductPrice.is_active == True
            ).all()
        except Exception as e:
            logger.error(f"Error getting product prices: {str(e)}")
            return []

    def create_product_review(self, data: Dict[str, Any]) -> Optional[ProductReview]:
        """ایجاد نظر محصول"""
        try:
            review = ProductReview(**data)
            self.db.add(review)
            self.db.commit()
            self.db.refresh(review)
            return review
        except Exception as e:
            logger.error(f"Error creating product review: {str(e)}")
            self.db.rollback()
            return None

    def get_product_reviews(self, product_id: int, approved_only: bool = True) -> List[ProductReview]:
        """دریافت نظرات محصول"""
        try:
            query = self.db.query(ProductReview).filter(
                ProductReview.product_id == product_id
            )
            if approved_only:
                query = query.filter(ProductReview.is_approved == True)
            return query.order_by(ProductReview.created_at.desc()).all()
        except Exception as e:
            logger.error(f"Error getting product reviews: {str(e)}")
            return []

    def create_product_image(self, data: Dict[str, Any]) -> Optional[ProductImage]:
        """ایجاد تصویر محصول"""
        try:
            image = ProductImage(**data)
            self.db.add(image)
            self.db.commit()
            self.db.refresh(image)
            return image
        except Exception as e:
            logger.error(f"Error creating product image: {str(e)}")
            self.db.rollback()
            return None

    def get_product_images(self, product_id: int) -> List[ProductImage]:
        """دریافت تصاویر محصول"""
        try:
            return self.db.query(ProductImage).filter(
                ProductImage.product_id == product_id,
                ProductImage.is_active == True
            ).order_by(ProductImage.sort_order).all()
        except Exception as e:
            logger.error(f"Error getting product images: {str(e)}")
            return []

    def search_products(self, query: str, category_id: Optional[int] = None) -> List[Product]:
        """جستجوی محصولات"""
        try:
            search_query = self.db.query(Product).filter(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.product_code.ilike(f"%{query}%"),
                    Product.sku.ilike(f"%{query}%")
                )
            )
            if category_id:
                search_query = search_query.filter(Product.category_id == category_id)
            return search_query.all()
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []

    def get_products_by_category(self, category_id: int, status: Optional[str] = None) -> List[Product]:
        """دریافت محصولات یک دسته‌بندی"""
        try:
            query = self.db.query(Product).filter(
                Product.category_id == category_id
            )
            if status:
                query = query.filter(Product.status == status)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting products by category: {str(e)}")
            return []

    def get_products_by_sales_rep(self, sales_rep_id: int, status: Optional[str] = None) -> List[Product]:
        """دریافت محصولات نماینده فروش"""
        try:
            query = self.db.query(Product).filter(
                Product.sales_rep_id == sales_rep_id
            )
            if status:
                query = query.filter(Product.status == status)
            return query.all()
        except Exception as e:
            logger.error(f"Error getting products by sales rep: {str(e)}")
            return []

    def get_product_statistics(self, product_id: int) -> Dict[str, Any]:
        """دریافت آمار محصول"""
        try:
            product = self.get_product(product_id)
            if not product:
                return {}

            # اینجا باید منطق محاسبه آمار محصول پیاده‌سازی شود
            return {
                "total_sales": 0,
                "total_revenue": 0.0,
                "average_rating": 0.0,
                "total_reviews": 0,
                "stock_level": 0,
                "stock_value": 0.0,
                "total_orders": 0,
                "return_rate": 0.0
            }
        except Exception as e:
            logger.error(f"Error getting product statistics: {str(e)}")
            return {} 