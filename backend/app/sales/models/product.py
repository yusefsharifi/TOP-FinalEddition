from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Text, Table
from sqlalchemy.orm import relationship
from app.database import Base

class ProductType(Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    SERVICE = "service"
    SUBSCRIPTION = "subscription"

class ProductStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    DRAFT = "draft"

class ProductCategory(Base):
    """مدل دسته‌بندی محصولات"""
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("product_categories.id"))
    level = Column(Integer, default=0)
    path = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    parent = relationship("ProductCategory", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")

class Product(Base):
    """مدل محصول"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    product_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default=ProductStatus.DRAFT.value)
    
    # اطلاعات قیمت
    base_price = Column(Float, nullable=False)
    sale_price = Column(Float)
    cost_price = Column(Float)
    tax_rate = Column(Float, default=0.0)
    
    # اطلاعات موجودی
    sku = Column(String(50), unique=True)
    barcode = Column(String(50))
    weight = Column(Float)
    dimensions = Column(JSON)  # طول، عرض، ارتفاع
    unit = Column(String(50))
    min_stock_level = Column(Integer, default=0)
    max_stock_level = Column(Integer)
    
    # اطلاعات دسته‌بندی
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    
    # اطلاعات فروش
    sales_rep_id = Column(Integer, ForeignKey("users.id"))
    commission_rate = Column(Float, default=0.0)
    
    # اطلاعات اضافی
    features = Column(JSON)  # ویژگی‌های محصول
    specifications = Column(JSON)  # مشخصات فنی
    images = Column(JSON)  # آدرس تصاویر محصول
    documents = Column(JSON)  # اسناد مرتبط
    tags = Column(JSON)  # برچسب‌ها
    custom_fields = Column(JSON)  # فیلدهای سفارشی
    
    # اطلاعات سیستم
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sale_at = Column(DateTime)
    
    # روابط
    category = relationship("ProductCategory", back_populates="products")
    sales_rep = relationship("User", foreign_keys=[sales_rep_id])
    creator = relationship("User", foreign_keys=[created_by])
    variants = relationship("ProductVariant", back_populates="product")
    inventory_items = relationship("InventoryItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    subscription_items = relationship("SubscriptionItem", back_populates="product")

class ProductVariant(Base):
    """مدل تنوع محصول"""
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    sku = Column(String(50), unique=True)
    barcode = Column(String(50))
    
    # قیمت‌ها
    base_price = Column(Float)
    sale_price = Column(Float)
    cost_price = Column(Float)
    
    # ویژگی‌ها
    attributes = Column(JSON)  # ویژگی‌های تنوع
    images = Column(JSON)  # تصاویر تنوع
    
    # موجودی
    weight = Column(Float)
    dimensions = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # روابط
    product = relationship("Product", back_populates="variants")
    inventory_items = relationship("InventoryItem", back_populates="variant")

class ProductPrice(Base):
    """مدل قیمت‌های محصول"""
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price_type = Column(String(50), nullable=False)  # retail, wholesale, special
    price = Column(Float, nullable=False)
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    product = relationship("Product")

class ProductReview(Base):
    """مدل نظرات محصول"""
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(200))
    content = Column(Text)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # روابط
    product = relationship("Product")
    customer = relationship("Customer")

class ProductImage(Base):
    """مدل تصاویر محصول"""
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    image_type = Column(String(50))  # main, gallery, thumbnail
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # روابط
    product = relationship("Product") 