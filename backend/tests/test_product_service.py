import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.sales.models.product import (
    Product, ProductCategory, ProductVariant,
    ProductPrice, ProductReview, ProductImage,
    ProductType, ProductStatus
)
from app.sales.services.product_service import ProductService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class TestProductService(unittest.TestCase):
    def setUp(self):
        """راه‌اندازی تست"""
        # ایجاد دیتابیس تست
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # ایجاد سرویس
        self.service = ProductService(self.session)
        
        # ایجاد داده‌های تست
        self._create_test_data()
    
    def tearDown(self):
        """پاکسازی تست"""
        self.session.close()
    
    def _create_test_data(self):
        """ایجاد داده‌های تست"""
        # ایجاد دسته‌بندی تست
        self.test_category = ProductCategory(
            name="دسته‌بندی تست",
            description="توضیحات دسته‌بندی تست"
        )
        self.session.add(self.test_category)
        self.session.commit()
        
        # ایجاد محصول تست
        self.test_product = Product(
            product_code="PROD-001",
            name="محصول تست",
            description="توضیحات محصول تست",
            product_type=ProductType.PHYSICAL.value,
            status=ProductStatus.ACTIVE.value,
            base_price=1000.0,
            category_id=self.test_category.id,
            created_by=1
        )
        self.session.add(self.test_product)
        self.session.commit()
        
        # ایجاد تنوع محصول تست
        self.test_variant = ProductVariant(
            product_id=self.test_product.id,
            variant_code="VAR-001",
            name="تنوع تست",
            sku="SKU-001",
            base_price=1100.0
        )
        self.session.add(self.test_variant)
        self.session.commit()
    
    def test_create_product(self):
        """تست ایجاد محصول"""
        data = {
            "product_code": "PROD-002",
            "name": "محصول تست 2",
            "description": "توضیحات محصول تست 2",
            "product_type": ProductType.PHYSICAL.value,
            "status": ProductStatus.ACTIVE.value,
            "base_price": 2000.0,
            "category_id": self.test_category.id,
            "created_by": 1
        }
        product = self.service.create_product(data)
        self.assertIsNotNone(product)
        self.assertEqual(product.product_code, "PROD-002")
    
    def test_get_product(self):
        """تست دریافت محصول"""
        product = self.service.get_product(self.test_product.id)
        self.assertIsNotNone(product)
        self.assertEqual(product.id, self.test_product.id)
    
    def test_update_product(self):
        """تست به‌روزرسانی محصول"""
        data = {
            "name": "محصول تست به‌روز شده",
            "description": "توضیحات به‌روز شده"
        }
        product = self.service.update_product(self.test_product.id, data)
        self.assertIsNotNone(product)
        self.assertEqual(product.name, "محصول تست به‌روز شده")
        self.assertEqual(product.description, "توضیحات به‌روز شده")
    
    def test_update_product_status(self):
        """تست به‌روزرسانی وضعیت محصول"""
        product = self.service.update_product_status(
            self.test_product.id, ProductStatus.INACTIVE.value
        )
        self.assertIsNotNone(product)
        self.assertEqual(product.status, ProductStatus.INACTIVE.value)
    
    def test_create_product_category(self):
        """تست ایجاد دسته‌بندی محصول"""
        data = {
            "name": "دسته‌بندی تست 2",
            "description": "توضیحات دسته‌بندی تست 2"
        }
        category = self.service.create_product_category(data)
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "دسته‌بندی تست 2")
    
    def test_get_product_category(self):
        """تست دریافت دسته‌بندی محصول"""
        category = self.service.get_product_category(self.test_category.id)
        self.assertIsNotNone(category)
        self.assertEqual(category.id, self.test_category.id)
    
    def test_create_product_variant(self):
        """تست ایجاد تنوع محصول"""
        data = {
            "product_id": self.test_product.id,
            "variant_code": "VAR-002",
            "name": "تنوع تست 2",
            "sku": "SKU-002",
            "base_price": 1200.0
        }
        variant = self.service.create_product_variant(data)
        self.assertIsNotNone(variant)
        self.assertEqual(variant.variant_code, "VAR-002")
    
    def test_get_product_variant(self):
        """تست دریافت تنوع محصول"""
        variant = self.service.get_product_variant(self.test_variant.id)
        self.assertIsNotNone(variant)
        self.assertEqual(variant.id, self.test_variant.id)
    
    def test_create_product_price(self):
        """تست ایجاد قیمت محصول"""
        data = {
            "product_id": self.test_product.id,
            "price_type": "retail",
            "price": 1500.0,
            "min_quantity": 1,
            "max_quantity": 10
        }
        price = self.service.create_product_price(data)
        self.assertIsNotNone(price)
        self.assertEqual(price.price, 1500.0)
    
    def test_get_product_prices(self):
        """تست دریافت قیمت‌های محصول"""
        # ابتدا یک قیمت ایجاد می‌کنیم
        price_data = {
            "product_id": self.test_product.id,
            "price_type": "retail",
            "price": 1500.0,
            "min_quantity": 1,
            "max_quantity": 10
        }
        self.service.create_product_price(price_data)
        
        # سپس قیمت‌ها را دریافت می‌کنیم
        prices = self.service.get_product_prices(self.test_product.id)
        self.assertIsNotNone(prices)
        self.assertIsInstance(prices, list)
        self.assertEqual(len(prices), 1)
    
    def test_create_product_review(self):
        """تست ایجاد نظر محصول"""
        data = {
            "product_id": self.test_product.id,
            "customer_id": 1,
            "rating": 5,
            "title": "نظر تست",
            "content": "محتوی نظر تست"
        }
        review = self.service.create_product_review(data)
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
    
    def test_get_product_reviews(self):
        """تست دریافت نظرات محصول"""
        # ابتدا یک نظر ایجاد می‌کنیم
        review_data = {
            "product_id": self.test_product.id,
            "customer_id": 1,
            "rating": 5,
            "title": "نظر تست",
            "content": "محتوی نظر تست"
        }
        self.service.create_product_review(review_data)
        
        # سپس نظرات را دریافت می‌کنیم
        reviews = self.service.get_product_reviews(self.test_product.id)
        self.assertIsNotNone(reviews)
        self.assertIsInstance(reviews, list)
        self.assertEqual(len(reviews), 1)
    
    def test_create_product_image(self):
        """تست ایجاد تصویر محصول"""
        data = {
            "product_id": self.test_product.id,
            "image_url": "http://example.com/image.jpg",
            "image_type": "main",
            "sort_order": 1
        }
        image = self.service.create_product_image(data)
        self.assertIsNotNone(image)
        self.assertEqual(image.image_url, "http://example.com/image.jpg")
    
    def test_get_product_images(self):
        """تست دریافت تصاویر محصول"""
        # ابتدا یک تصویر ایجاد می‌کنیم
        image_data = {
            "product_id": self.test_product.id,
            "image_url": "http://example.com/image.jpg",
            "image_type": "main",
            "sort_order": 1
        }
        self.service.create_product_image(image_data)
        
        # سپس تصاویر را دریافت می‌کنیم
        images = self.service.get_product_images(self.test_product.id)
        self.assertIsNotNone(images)
        self.assertIsInstance(images, list)
        self.assertEqual(len(images), 1)
    
    def test_search_products(self):
        """تست جستجوی محصولات"""
        products = self.service.search_products("محصول تست")
        self.assertIsNotNone(products)
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
    
    def test_get_products_by_category(self):
        """تست دریافت محصولات یک دسته‌بندی"""
        products = self.service.get_products_by_category(self.test_category.id)
        self.assertIsNotNone(products)
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
    
    def test_get_products_by_sales_rep(self):
        """تست دریافت محصولات نماینده فروش"""
        # ابتدا محصول را به یک نماینده فروش اختصاص می‌دهیم
        self.test_product.sales_rep_id = 1
        self.session.commit()
        
        # سپس محصولات نماینده را دریافت می‌کنیم
        products = self.service.get_products_by_sales_rep(1)
        self.assertIsNotNone(products)
        self.assertIsInstance(products, list)
        self.assertEqual(len(products), 1)
    
    def test_get_product_statistics(self):
        """تست دریافت آمار محصول"""
        statistics = self.service.get_product_statistics(self.test_product.id)
        self.assertIsNotNone(statistics)
        self.assertIsInstance(statistics, dict) 