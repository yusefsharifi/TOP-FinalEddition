from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
import json
import os
import uuid
import numpy as np
from datetime import datetime, timedelta

class SalesOrderStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class SalesOrderType(Enum):
    REGULAR = "regular"
    RUSH = "rush"
    BACKORDER = "backorder"
    PREORDER = "preorder"
    SUBSCRIPTION = "subscription"

class PaymentStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class PaymentTerm(Enum):
    IMMEDIATE = "immediate"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_45 = "net_45"
    NET_60 = "net_60"
    END_OF_MONTH = "end_of_month"

class TaxType(Enum):
    VAT = "vat"
    SALES_TAX = "sales_tax"
    EXCISE_TAX = "excise_tax"

class CustomerType(Enum):
    REGULAR = "regular"
    VIP = "vip"
    WHOLESALE = "wholesale"
    DISTRIBUTOR = "distributor"
    RESELLER = "reseller"

class CustomerStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING = "pending"

class DeliveryStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

class ReturnStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ReturnReason(Enum):
    WRONG_ITEM = "wrong_item"
    DAMAGED = "damaged"
    QUALITY_ISSUE = "quality_issue"
    NOT_AS_DESCRIBED = "not_as_described"
    CUSTOMER_CHANGED_MIND = "customer_changed_mind"
    OTHER = "other"

@dataclass
class Customer:
    id: str
    code: str
    name: str
    type: CustomerType
    status: CustomerStatus
    contact_person: str
    contact_phone: str
    email: str
    address: str
    tax_number: Optional[str]
    payment_terms: PaymentTerm
    credit_limit: Decimal
    currency: str
    sales_representative: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class CustomerGroup:
    id: str
    name: str
    description: str
    discount_rate: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesOrder:
    id: str
    order_number: str
    type: SalesOrderType
    status: SalesOrderStatus
    customer_id: str
    order_date: date
    delivery_date: date
    payment_terms: PaymentTerm
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesOrderItem:
    id: str
    order_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
    discount_rate: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesInvoice:
    id: str
    invoice_number: str
    order_id: str
    invoice_date: date
    due_date: date
    customer_id: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    currency: str
    status: PaymentStatus
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesPayment:
    id: str
    invoice_id: str
    payment_date: date
    amount: Decimal
    currency: str
    payment_method: str
    reference_number: str
    status: PaymentStatus
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesDelivery:
    id: str
    delivery_number: str
    order_id: str
    delivery_date: date
    status: DeliveryStatus
    carrier: str
    tracking_number: str
    shipping_address: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesReturn:
    id: str
    return_number: str
    order_id: str
    return_date: date
    customer_id: str
    status: ReturnStatus
    reason: ReturnReason
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesReturnItem:
    id: str
    return_id: str
    order_item_id: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    reason: ReturnReason
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesAnalysis:
    id: str
    customer_id: str
    period_start: date
    period_end: date
    total_orders: int
    total_amount: Decimal
    currency: str
    average_order_value: Decimal
    payment_performance: Decimal
    return_rate: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesForecast:
    id: str
    item_id: str
    period_start: date
    period_end: date
    forecasted_quantity: Decimal
    confidence_level: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesTarget:
    id: str
    sales_representative: str
    period_start: date
    period_end: date
    target_amount: Decimal
    currency: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesPromotion:
    id: str
    name: str
    description: str
    start_date: date
    end_date: date
    discount_type: str
    discount_value: Decimal
    min_purchase_amount: Decimal
    max_discount_amount: Decimal
    is_active: bool
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesQuotation:
    id: str
    quotation_number: str
    customer_id: str
    valid_until: date
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    currency: str
    status: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SalesQuotationItem:
    id: str
    quotation_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
    discount_rate: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class SalesManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.customers: Dict[str, Customer] = {}
        self.customer_groups: Dict[str, CustomerGroup] = {}
        self.orders: Dict[str, SalesOrder] = {}
        self.order_items: Dict[str, SalesOrderItem] = {}
        self.invoices: Dict[str, SalesInvoice] = {}
        self.payments: Dict[str, SalesPayment] = {}
        self.deliveries: Dict[str, SalesDelivery] = {}
        self.returns: Dict[str, SalesReturn] = {}
        self.return_items: Dict[str, SalesReturnItem] = {}
        self.analyses: Dict[str, SalesAnalysis] = {}
        self.forecasts: Dict[str, SalesForecast] = {}
        self.targets: Dict[str, SalesTarget] = {}
        self.promotions: Dict[str, SalesPromotion] = {}
        self.quotations: Dict[str, SalesQuotation] = {}
        self.quotation_items: Dict[str, SalesQuotationItem] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load customers from file
        self.load_customers()
    
    def create_directories(self):
        """Create necessary directories for sales management"""
        try:
            # Create sales data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'sales_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create sales reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'sales_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("Sales management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_customers(self):
        """Load customers from JSON file"""
        try:
            customers_file = os.path.join(os.path.dirname(__file__), 'customers.json')
            if os.path.exists(customers_file):
                with open(customers_file, 'r', encoding='utf-8') as f:
                    customers_data = json.load(f)
                    for customer_data in customers_data:
                        customer = Customer(
                            id=customer_data['id'],
                            code=customer_data['code'],
                            name=customer_data['name'],
                            type=CustomerType(customer_data['type']),
                            status=CustomerStatus(customer_data['status']),
                            contact_person=customer_data['contact_person'],
                            contact_phone=customer_data['contact_phone'],
                            email=customer_data['email'],
                            address=customer_data['address'],
                            tax_number=customer_data.get('tax_number'),
                            payment_terms=PaymentTerm(customer_data['payment_terms']),
                            credit_limit=Decimal(str(customer_data['credit_limit'])),
                            currency=customer_data['currency'],
                            sales_representative=customer_data['sales_representative'],
                            notes=customer_data['notes'],
                            created_by=customer_data['created_by']
                        )
                        self.customers[customer.id] = customer
                self.logger.info("Customers loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading customers: {str(e)}")
    
    def add_customer(self, customer: Customer) -> bool:
        """Add new customer"""
        try:
            if customer.id in self.customers:
                self.logger.warning(f"Customer with ID {customer.id} already exists")
                return False
            
            self.customers[customer.id] = customer
            self.logger.info(f"Customer added: {customer.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding customer: {str(e)}")
            return False
    
    def update_customer(self, customer_id: str, updates: Dict[str, Any]) -> bool:
        """Update customer details"""
        try:
            customer = self.customers.get(customer_id)
            if not customer:
                self.logger.error(f"Customer {customer_id} not found")
                return False
            
            # Update customer attributes
            for key, value in updates.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            customer.updated_at = datetime.now()
            self.logger.info(f"Customer updated: {customer.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating customer: {str(e)}")
            return False
    
    def add_sales_order(self, order: SalesOrder) -> bool:
        """Add new sales order"""
        try:
            if order.id in self.orders:
                self.logger.warning(f"Order with ID {order.id} already exists")
                return False
            
            if order.customer_id not in self.customers:
                self.logger.error(f"Customer {order.customer_id} not found")
                return False
            
            self.orders[order.id] = order
            self.logger.info(f"Order added: {order.order_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding order: {str(e)}")
            return False
    
    def add_order_item(self, item: SalesOrderItem) -> bool:
        """Add order item"""
        try:
            if item.id in self.order_items:
                self.logger.warning(f"Order item with ID {item.id} already exists")
                return False
            
            if item.order_id not in self.orders:
                self.logger.error(f"Order {item.order_id} not found")
                return False
            
            self.order_items[item.id] = item
            self.logger.info(f"Order item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding order item: {str(e)}")
            return False
    
    def add_sales_invoice(self, invoice: SalesInvoice) -> bool:
        """Add sales invoice"""
        try:
            if invoice.id in self.invoices:
                self.logger.warning(f"Invoice with ID {invoice.id} already exists")
                return False
            
            if invoice.order_id not in self.orders:
                self.logger.error(f"Order {invoice.order_id} not found")
                return False
            
            if invoice.customer_id not in self.customers:
                self.logger.error(f"Customer {invoice.customer_id} not found")
                return False
            
            self.invoices[invoice.id] = invoice
            self.logger.info(f"Invoice added: {invoice.invoice_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding invoice: {str(e)}")
            return False
    
    def add_sales_payment(self, payment: SalesPayment) -> bool:
        """Add sales payment"""
        try:
            if payment.id in self.payments:
                self.logger.warning(f"Payment with ID {payment.id} already exists")
                return False
            
            if payment.invoice_id not in self.invoices:
                self.logger.error(f"Invoice {payment.invoice_id} not found")
                return False
            
            self.payments[payment.id] = payment
            self.logger.info(f"Payment added: {payment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding payment: {str(e)}")
            return False
    
    def add_sales_delivery(self, delivery: SalesDelivery) -> bool:
        """Add sales delivery"""
        try:
            if delivery.id in self.deliveries:
                self.logger.warning(f"Delivery with ID {delivery.id} already exists")
                return False
            
            if delivery.order_id not in self.orders:
                self.logger.error(f"Order {delivery.order_id} not found")
                return False
            
            self.deliveries[delivery.id] = delivery
            self.logger.info(f"Delivery added: {delivery.delivery_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding delivery: {str(e)}")
            return False
    
    def add_sales_return(self, return_order: SalesReturn) -> bool:
        """Add sales return"""
        try:
            if return_order.id in self.returns:
                self.logger.warning(f"Return with ID {return_order.id} already exists")
                return False
            
            if return_order.order_id not in self.orders:
                self.logger.error(f"Order {return_order.order_id} not found")
                return False
            
            if return_order.customer_id not in self.customers:
                self.logger.error(f"Customer {return_order.customer_id} not found")
                return False
            
            self.returns[return_order.id] = return_order
            self.logger.info(f"Return added: {return_order.return_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding return: {str(e)}")
            return False
    
    def add_return_item(self, item: SalesReturnItem) -> bool:
        """Add return item"""
        try:
            if item.id in self.return_items:
                self.logger.warning(f"Return item with ID {item.id} already exists")
                return False
            
            if item.return_id not in self.returns:
                self.logger.error(f"Return {item.return_id} not found")
                return False
            
            if item.order_item_id not in self.order_items:
                self.logger.error(f"Order item {item.order_item_id} not found")
                return False
            
            self.return_items[item.id] = item
            self.logger.info(f"Return item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding return item: {str(e)}")
            return False
    
    def add_sales_analysis(self, analysis: SalesAnalysis) -> bool:
        """Add sales analysis"""
        try:
            if analysis.id in self.analyses:
                self.logger.warning(f"Analysis with ID {analysis.id} already exists")
                return False
            
            if analysis.customer_id not in self.customers:
                self.logger.error(f"Customer {analysis.customer_id} not found")
                return False
            
            self.analyses[analysis.id] = analysis
            self.logger.info(f"Analysis added: {analysis.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding analysis: {str(e)}")
            return False
    
    def calculate_customer_performance(self, customer_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate customer performance metrics"""
        try:
            # Get customer's orders for period
            period_orders = [
                order for order in self.orders.values()
                if order.customer_id == customer_id
                and start_date <= order.order_date <= end_date
            ]
            
            # Get customer's returns for period
            period_returns = [
                return_order for return_order in self.returns.values()
                if return_order.customer_id == customer_id
                and start_date <= return_order.return_date <= end_date
            ]
            
            # Calculate metrics
            metrics = {
                "total_orders": len(period_orders),
                "total_amount": sum(order.total_amount for order in period_orders),
                "currency": period_orders[0].currency if period_orders else None,
                "average_order_value": self.calculate_average_order_value(period_orders),
                "payment_performance": self.calculate_payment_performance(customer_id, start_date, end_date),
                "return_rate": self.calculate_return_rate(period_orders, period_returns)
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating customer performance: {str(e)}")
            return {}
    
    def calculate_average_order_value(self, orders: List[SalesOrder]) -> Decimal:
        """Calculate average order value"""
        try:
            if not orders:
                return Decimal('0')
            
            total_amount = sum(order.total_amount for order in orders)
            return total_amount / len(orders)
        except Exception as e:
            self.logger.error(f"Error calculating average order value: {str(e)}")
            return Decimal('0')
    
    def calculate_payment_performance(self, customer_id: str, start_date: date, end_date: date) -> Decimal:
        """Calculate payment performance"""
        try:
            # Get customer's invoices for period
            period_invoices = [
                invoice for invoice in self.invoices.values()
                if invoice.customer_id == customer_id
                and start_date <= invoice.invoice_date <= end_date
            ]
            
            if not period_invoices:
                return Decimal('1')
            
            # Calculate total amount and paid amount
            total_amount = sum(invoice.total_amount for invoice in period_invoices)
            paid_amount = sum(
                sum(payment.amount for payment in self.payments.values() if payment.invoice_id == invoice.id)
                for invoice in period_invoices
            )
            
            return Decimal(str(paid_amount / total_amount))
        except Exception as e:
            self.logger.error(f"Error calculating payment performance: {str(e)}")
            return Decimal('0')
    
    def calculate_return_rate(self, orders: List[SalesOrder], returns: List[SalesReturn]) -> Decimal:
        """Calculate return rate"""
        try:
            if not orders:
                return Decimal('0')
            
            total_amount = sum(order.total_amount for order in orders)
            return_amount = sum(return_order.total_amount for return_order in returns)
            
            return Decimal(str(return_amount / total_amount))
        except Exception as e:
            self.logger.error(f"Error calculating return rate: {str(e)}")
            return Decimal('0')
    
    def generate_sales_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate sales report"""
        try:
            # Get orders for period
            period_orders = [
                order for order in self.orders.values()
                if start_date <= order.order_date <= end_date
            ]
            
            # Get deliveries for period
            period_deliveries = [
                delivery for delivery in self.deliveries.values()
                if start_date <= delivery.delivery_date <= end_date
            ]
            
            # Get returns for period
            period_returns = [
                return_order for return_order in self.returns.values()
                if start_date <= return_order.return_date <= end_date
            ]
            
            # Calculate report metrics
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "orders": {
                    "total": len(period_orders),
                    "by_status": self.calculate_orders_by_status(period_orders),
                    "by_customer": self.calculate_orders_by_customer(period_orders),
                    "by_type": self.calculate_orders_by_type(period_orders)
                },
                "deliveries": {
                    "total": len(period_deliveries),
                    "by_status": self.calculate_deliveries_by_status(period_deliveries)
                },
                "returns": {
                    "total": len(period_returns),
                    "total_amount": sum(return_order.total_amount for return_order in period_returns),
                    "by_reason": self.calculate_returns_by_reason(period_returns)
                },
                "payments": {
                    "total": sum(payment.amount for payment in self.payments.values() if start_date <= payment.payment_date <= end_date),
                    "by_status": self.calculate_payments_by_status(start_date, end_date)
                },
                "customer_performance": self.calculate_customer_performance_metrics(start_date, end_date)
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating sales report: {str(e)}")
            return {}
    
    def calculate_orders_by_status(self, orders: List[SalesOrder]) -> Dict[str, int]:
        """Calculate orders by status"""
        try:
            status_counts = {}
            for status in SalesOrderStatus:
                status_counts[status.value] = len([
                    order for order in orders
                    if order.status == status
                ])
            return status_counts
        except Exception as e:
            self.logger.error(f"Error calculating orders by status: {str(e)}")
            return {}
    
    def calculate_orders_by_customer(self, orders: List[SalesOrder]) -> Dict[str, Dict[str, Any]]:
        """Calculate orders by customer"""
        try:
            customer_orders = {}
            for order in orders:
                if order.customer_id not in customer_orders:
                    customer_orders[order.customer_id] = {
                        "count": 0,
                        "total_amount": Decimal('0'),
                        "currency": order.currency
                    }
                customer_orders[order.customer_id]["count"] += 1
                customer_orders[order.customer_id]["total_amount"] += order.total_amount
            return customer_orders
        except Exception as e:
            self.logger.error(f"Error calculating orders by customer: {str(e)}")
            return {}
    
    def calculate_orders_by_type(self, orders: List[SalesOrder]) -> Dict[str, int]:
        """Calculate orders by type"""
        try:
            type_counts = {}
            for order_type in SalesOrderType:
                type_counts[order_type.value] = len([
                    order for order in orders
                    if order.type == order_type
                ])
            return type_counts
        except Exception as e:
            self.logger.error(f"Error calculating orders by type: {str(e)}")
            return {}
    
    def calculate_deliveries_by_status(self, deliveries: List[SalesDelivery]) -> Dict[str, int]:
        """Calculate deliveries by status"""
        try:
            status_counts = {}
            for status in DeliveryStatus:
                status_counts[status.value] = len([
                    delivery for delivery in deliveries
                    if delivery.status == status
                ])
            return status_counts
        except Exception as e:
            self.logger.error(f"Error calculating deliveries by status: {str(e)}")
            return {}
    
    def calculate_returns_by_reason(self, returns: List[SalesReturn]) -> Dict[str, int]:
        """Calculate returns by reason"""
        try:
            reason_counts = {}
            for reason in ReturnReason:
                reason_counts[reason.value] = len([
                    return_order for return_order in returns
                    if return_order.reason == reason
                ])
            return reason_counts
        except Exception as e:
            self.logger.error(f"Error calculating returns by reason: {str(e)}")
            return {}
    
    def calculate_payments_by_status(self, start_date: date, end_date: date) -> Dict[str, Decimal]:
        """Calculate payments by status"""
        try:
            status_amounts = {}
            for status in PaymentStatus:
                status_amounts[status.value] = sum(
                    payment.amount
                    for payment in self.payments.values()
                    if payment.status == status
                    and start_date <= payment.payment_date <= end_date
                )
            return status_amounts
        except Exception as e:
            self.logger.error(f"Error calculating payments by status: {str(e)}")
            return {}
    
    def calculate_customer_performance_metrics(self, start_date: date, end_date: date) -> Dict[str, Dict[str, Any]]:
        """Calculate customer performance metrics"""
        try:
            metrics = {}
            for customer_id in self.customers:
                metrics[customer_id] = self.calculate_customer_performance(
                    customer_id,
                    start_date,
                    end_date
                )
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating customer performance metrics: {str(e)}")
            return {}
    
    def add_sales_forecast(self, forecast: SalesForecast) -> bool:
        """Add sales forecast"""
        try:
            if forecast.id in self.forecasts:
                self.logger.warning(f"Forecast with ID {forecast.id} already exists")
                return False
            
            self.forecasts[forecast.id] = forecast
            self.logger.info(f"Forecast added: {forecast.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding forecast: {str(e)}")
            return False
    
    def add_sales_target(self, target: SalesTarget) -> bool:
        """Add sales target"""
        try:
            if target.id in self.targets:
                self.logger.warning(f"Target with ID {target.id} already exists")
                return False
            
            self.targets[target.id] = target
            self.logger.info(f"Target added: {target.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding target: {str(e)}")
            return False
    
    def add_sales_promotion(self, promotion: SalesPromotion) -> bool:
        """Add sales promotion"""
        try:
            if promotion.id in self.promotions:
                self.logger.warning(f"Promotion with ID {promotion.id} already exists")
                return False
            
            self.promotions[promotion.id] = promotion
            self.logger.info(f"Promotion added: {promotion.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding promotion: {str(e)}")
            return False
    
    def add_sales_quotation(self, quotation: SalesQuotation) -> bool:
        """Add sales quotation"""
        try:
            if quotation.id in self.quotations:
                self.logger.warning(f"Quotation with ID {quotation.id} already exists")
                return False
            
            if quotation.customer_id not in self.customers:
                self.logger.error(f"Customer {quotation.customer_id} not found")
                return False
            
            self.quotations[quotation.id] = quotation
            self.logger.info(f"Quotation added: {quotation.quotation_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quotation: {str(e)}")
            return False
    
    def add_quotation_item(self, item: SalesQuotationItem) -> bool:
        """Add quotation item"""
        try:
            if item.id in self.quotation_items:
                self.logger.warning(f"Quotation item with ID {item.id} already exists")
                return False
            
            if item.quotation_id not in self.quotations:
                self.logger.error(f"Quotation {item.quotation_id} not found")
                return False
            
            self.quotation_items[item.id] = item
            self.logger.info(f"Quotation item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quotation item: {str(e)}")
            return False
    
    def convert_quotation_to_order(self, quotation_id: str) -> Dict[str, Any]:
        """Convert quotation to order"""
        try:
            quotation = self.quotations.get(quotation_id)
            if not quotation:
                self.logger.error(f"Quotation {quotation_id} not found")
                return {"success": False, "message": "Quotation not found"}
            
            # Create order
            order = SalesOrder(
                id=str(uuid.uuid4()),
                order_number=f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                type=SalesOrderType.REGULAR,
                status=SalesOrderStatus.PENDING,
                customer_id=quotation.customer_id,
                order_date=date.today(),
                delivery_date=date.today() + timedelta(days=7),
                payment_terms=quotation.payment_terms,
                subtotal=quotation.subtotal,
                discount_amount=quotation.discount_amount,
                tax_amount=quotation.tax_amount,
                shipping_amount=quotation.shipping_amount,
                total_amount=quotation.total_amount,
                currency=quotation.currency,
                notes=f"Converted from quotation {quotation.quotation_number}",
                created_by=quotation.created_by
            )
            
            # Add order
            if not self.add_sales_order(order):
                return {"success": False, "message": "Failed to add order"}
            
            # Get quotation items
            quotation_items = [
                item for item in self.quotation_items.values()
                if item.quotation_id == quotation_id
            ]
            
            # Create order items
            for quotation_item in quotation_items:
                order_item = SalesOrderItem(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    item_id=quotation_item.item_id,
                    quantity=quotation_item.quantity,
                    unit_price=quotation_item.unit_price,
                    discount_rate=quotation_item.discount_rate,
                    discount_amount=quotation_item.discount_amount,
                    tax_rate=quotation_item.tax_rate,
                    tax_amount=quotation_item.tax_amount,
                    total_amount=quotation_item.total_amount,
                    currency=quotation_item.currency,
                    delivery_date=order.delivery_date,
                    notes=quotation_item.notes,
                    created_by=quotation_item.created_by
                )
                
                if not self.add_order_item(order_item):
                    return {"success": False, "message": "Failed to add order item"}
            
            return {
                "success": True,
                "message": "Quotation converted to order successfully",
                "order_id": order.id
            }
        except Exception as e:
            self.logger.error(f"Error converting quotation to order: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def generate_customer_report(self, customer_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate customer report"""
        try:
            if customer_id not in self.customers:
                self.logger.error(f"Customer {customer_id} not found")
                return {}
            
            # Get customer's orders for period
            period_orders = [
                order for order in self.orders.values()
                if order.customer_id == customer_id
                and start_date <= order.order_date <= end_date
            ]
            
            # Get customer's returns for period
            period_returns = [
                return_order for return_order in self.returns.values()
                if return_order.customer_id == customer_id
                and start_date <= return_order.return_date <= end_date
            ]
            
            # Get customer's payments for period
            period_payments = [
                payment for payment in self.payments.values()
                if payment.invoice_id in [i.id for i in self.invoices.values() if i.customer_id == customer_id]
                and start_date <= payment.payment_date <= end_date
            ]
            
            # Calculate metrics
            report = {
                "customer_id": customer_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "orders": {
                    "total": len(period_orders),
                    "total_amount": sum(order.total_amount for order in period_orders),
                    "by_status": self.calculate_orders_by_status(period_orders)
                },
                "returns": {
                    "total": len(period_returns),
                    "total_amount": sum(return_order.total_amount for return_order in period_returns)
                },
                "payments": {
                    "total": sum(payment.amount for payment in period_payments),
                    "by_status": self.calculate_payments_by_status(start_date, end_date)
                },
                "performance": {
                    "average_order_value": self.calculate_average_order_value(period_orders),
                    "payment_performance": self.calculate_payment_performance(customer_id, start_date, end_date),
                    "return_rate": self.calculate_return_rate(period_orders, period_returns)
                }
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating customer report: {str(e)}")
            return {} 