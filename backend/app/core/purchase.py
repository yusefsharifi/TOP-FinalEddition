from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
import os
import uuid
import numpy as np
from datetime import datetime, timedelta

class PurchaseOrderStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    CLOSED = "closed"

class PurchaseOrderType(Enum):
    REGULAR = "regular"
    EMERGENCY = "emergency"
    BLANKET = "blanket"
    CONTRACT = "contract"
    CONSIGNMENT = "consignment"

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
    IMPORT_DUTY = "import_duty"
    EXCISE_TAX = "excise_tax"

class RFQStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"

class TenderStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    EVALUATED = "evaluated"
    AWARDED = "awarded"
    CANCELLED = "cancelled"

class ContractStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"

class QualityStatus(Enum):
    PENDING = "pending"
    INSPECTED = "inspected"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PARTIALLY_ACCEPTED = "partially_accepted"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Supplier:
    id: str
    code: str
    name: str
    type: str
    contact_person: str
    contact_phone: str
    email: str
    address: str
    tax_number: Optional[str]
    payment_terms: PaymentTerm
    credit_limit: Decimal
    currency: str
    is_active: bool = True
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseOrder:
    id: str
    order_number: str
    type: PurchaseOrderType
    status: PurchaseOrderStatus
    supplier_id: str
    order_date: date
    delivery_date: date
    payment_terms: PaymentTerm
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseOrderItem:
    id: str
    order_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
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
class PurchaseReceipt:
    id: str
    receipt_number: str
    order_id: str
    receipt_date: date
    supplier_id: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseReceiptItem:
    id: str
    receipt_id: str
    order_item_id: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchasePayment:
    id: str
    receipt_id: str
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
class PurchaseReturn:
    id: str
    return_number: str
    receipt_id: str
    return_date: date
    supplier_id: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    reason: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseReturnItem:
    id: str
    return_id: str
    receipt_item_id: str
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    reason: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseInvoice:
    id: str
    invoice_number: str
    receipt_id: str
    invoice_date: date
    due_date: date
    supplier_id: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    currency: str
    status: PaymentStatus
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class PurchaseAnalysis:
    id: str
    supplier_id: str
    period_start: date
    period_end: date
    total_orders: int
    total_amount: Decimal
    currency: str
    average_delivery_time: int
    on_time_delivery_rate: Decimal
    quality_rate: Decimal
    payment_performance: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class RFQ:
    id: str
    number: str
    title: str
    description: str
    status: RFQStatus
    publish_date: date
    closing_date: date
    currency: str
    total_amount: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class RFQItem:
    id: str
    rfq_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class RFQResponse:
    id: str
    rfq_id: str
    supplier_id: str
    response_date: date
    total_amount: Decimal
    currency: str
    delivery_terms: str
    payment_terms: str
    validity_period: int
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class RFQResponseItem:
    id: str
    response_id: str
    rfq_item_id: str
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Tender:
    id: str
    number: str
    title: str
    description: str
    status: TenderStatus
    publish_date: date
    closing_date: date
    currency: str
    total_amount: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TenderItem:
    id: str
    tender_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TenderResponse:
    id: str
    tender_id: str
    supplier_id: str
    response_date: date
    total_amount: Decimal
    currency: str
    delivery_terms: str
    payment_terms: str
    validity_period: int
    technical_score: Decimal
    financial_score: Decimal
    total_score: Decimal
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TenderResponseItem:
    id: str
    response_id: str
    tender_item_id: str
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Contract:
    id: str
    number: str
    title: str
    supplier_id: str
    status: ContractStatus
    start_date: date
    end_date: date
    currency: str
    total_amount: Decimal
    payment_terms: str
    delivery_terms: str
    warranty_period: int
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class ContractItem:
    id: str
    contract_id: str
    item_id: str
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    currency: str
    delivery_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class QualityStandard:
    id: str
    code: str
    name: str
    description: str
    requirements: List[str]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class QualityInspection:
    id: str
    receipt_id: str
    inspector_id: str
    inspection_date: date
    status: QualityStatus
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class QualityInspectionItem:
    id: str
    inspection_id: str
    receipt_item_id: str
    quantity: Decimal
    status: QualityStatus
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class QualityCertificate:
    id: str
    supplier_id: str
    standard_id: str
    certificate_number: str
    issue_date: date
    expiry_date: date
    issuing_body: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class InventoryControl:
    id: str
    item_id: str
    warehouse_id: str
    min_quantity: Decimal
    max_quantity: Decimal
    reorder_point: Decimal
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Cost:
    id: str
    receipt_id: str
    cost_type: str
    amount: Decimal
    currency: str
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Risk:
    id: str
    supplier_id: str
    risk_type: str
    level: RiskLevel
    description: str
    impact: str
    probability: str
    mitigation: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Communication:
    id: str
    supplier_id: str
    type: str
    subject: str
    content: str
    date: date
    status: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Document:
    id: str
    supplier_id: str
    type: str
    title: str
    file_path: str
    version: str
    upload_date: date
    expiry_date: Optional[date]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Budget:
    id: str
    year: int
    category: str
    amount: Decimal
    currency: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class SupplierEvaluation:
    id: str
    supplier_id: str
    evaluation_date: date
    criteria: Dict[str, Decimal]
    total_score: Decimal
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class PurchaseManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.suppliers: Dict[str, Supplier] = {}
        self.orders: Dict[str, PurchaseOrder] = {}
        self.order_items: Dict[str, PurchaseOrderItem] = {}
        self.receipts: Dict[str, PurchaseReceipt] = {}
        self.receipt_items: Dict[str, PurchaseReceiptItem] = {}
        self.payments: Dict[str, PurchasePayment] = {}
        self.returns: Dict[str, PurchaseReturn] = {}
        self.return_items: Dict[str, PurchaseReturnItem] = {}
        self.invoices: Dict[str, PurchaseInvoice] = {}
        self.analyses: Dict[str, PurchaseAnalysis] = {}
        
        # New dictionaries for advanced features
        self.rfqs: Dict[str, RFQ] = {}
        self.rfq_items: Dict[str, RFQItem] = {}
        self.rfq_responses: Dict[str, RFQResponse] = {}
        self.rfq_response_items: Dict[str, RFQResponseItem] = {}
        self.tenders: Dict[str, Tender] = {}
        self.tender_items: Dict[str, TenderItem] = {}
        self.tender_responses: Dict[str, TenderResponse] = {}
        self.tender_response_items: Dict[str, TenderResponseItem] = {}
        self.contracts: Dict[str, Contract] = {}
        self.contract_items: Dict[str, ContractItem] = {}
        self.quality_standards: Dict[str, QualityStandard] = {}
        self.quality_inspections: Dict[str, QualityInspection] = {}
        self.quality_inspection_items: Dict[str, QualityInspectionItem] = {}
        self.quality_certificates: Dict[str, QualityCertificate] = {}
        self.inventory_controls: Dict[str, InventoryControl] = {}
        self.costs: Dict[str, Cost] = {}
        self.risks: Dict[str, Risk] = {}
        self.communications: Dict[str, Communication] = {}
        self.documents: Dict[str, Document] = {}
        self.budgets: Dict[str, Budget] = {}
        self.supplier_evaluations: Dict[str, SupplierEvaluation] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load suppliers from file
        self.load_suppliers()
    
    def create_directories(self):
        """Create necessary directories for purchase management"""
        try:
            # Create purchase data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'purchase_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create purchase reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'purchase_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            self.logger.info("Purchase management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_suppliers(self):
        """Load suppliers from JSON file"""
        try:
            suppliers_file = os.path.join(os.path.dirname(__file__), 'suppliers.json')
            if os.path.exists(suppliers_file):
                with open(suppliers_file, 'r', encoding='utf-8') as f:
                    suppliers_data = json.load(f)
                    for supplier_data in suppliers_data:
                        supplier = Supplier(
                            id=supplier_data['id'],
                            code=supplier_data['code'],
                            name=supplier_data['name'],
                            type=supplier_data['type'],
                            contact_person=supplier_data['contact_person'],
                            contact_phone=supplier_data['contact_phone'],
                            email=supplier_data['email'],
                            address=supplier_data['address'],
                            tax_number=supplier_data.get('tax_number'),
                            payment_terms=PaymentTerm(supplier_data['payment_terms']),
                            credit_limit=Decimal(str(supplier_data['credit_limit'])),
                            currency=supplier_data['currency'],
                            is_active=supplier_data['is_active'],
                            created_by=supplier_data['created_by']
                        )
                        self.suppliers[supplier.id] = supplier
                self.logger.info("Suppliers loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading suppliers: {str(e)}")
    
    def add_supplier(self, supplier: Supplier) -> bool:
        """Add new supplier"""
        try:
            if supplier.id in self.suppliers:
                self.logger.warning(f"Supplier with ID {supplier.id} already exists")
                return False
            
            self.suppliers[supplier.id] = supplier
            self.logger.info(f"Supplier added: {supplier.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding supplier: {str(e)}")
            return False
    
    def update_supplier(self, supplier_id: str, updates: Dict[str, Any]) -> bool:
        """Update supplier details"""
        try:
            supplier = self.suppliers.get(supplier_id)
            if not supplier:
                self.logger.error(f"Supplier {supplier_id} not found")
                return False
            
            # Update supplier attributes
            for key, value in updates.items():
                if hasattr(supplier, key):
                    setattr(supplier, key, value)
            
            supplier.updated_at = datetime.now()
            self.logger.info(f"Supplier updated: {supplier.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating supplier: {str(e)}")
            return False
    
    def add_purchase_order(self, order: PurchaseOrder) -> bool:
        """Add new purchase order"""
        try:
            if order.id in self.orders:
                self.logger.warning(f"Order with ID {order.id} already exists")
                return False
            
            if order.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {order.supplier_id} not found")
                return False
            
            self.orders[order.id] = order
            self.logger.info(f"Order added: {order.order_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding order: {str(e)}")
            return False
    
    def add_order_item(self, item: PurchaseOrderItem) -> bool:
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
    
    def add_purchase_receipt(self, receipt: PurchaseReceipt) -> bool:
        """Add purchase receipt"""
        try:
            if receipt.id in self.receipts:
                self.logger.warning(f"Receipt with ID {receipt.id} already exists")
                return False
            
            if receipt.order_id not in self.orders:
                self.logger.error(f"Order {receipt.order_id} not found")
                return False
            
            if receipt.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {receipt.supplier_id} not found")
                return False
            
            self.receipts[receipt.id] = receipt
            self.logger.info(f"Receipt added: {receipt.receipt_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding receipt: {str(e)}")
            return False
    
    def add_receipt_item(self, item: PurchaseReceiptItem) -> bool:
        """Add receipt item"""
        try:
            if item.id in self.receipt_items:
                self.logger.warning(f"Receipt item with ID {item.id} already exists")
                return False
            
            if item.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {item.receipt_id} not found")
                return False
            
            if item.order_item_id not in self.order_items:
                self.logger.error(f"Order item {item.order_item_id} not found")
                return False
            
            self.receipt_items[item.id] = item
            self.logger.info(f"Receipt item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding receipt item: {str(e)}")
            return False
    
    def add_purchase_payment(self, payment: PurchasePayment) -> bool:
        """Add purchase payment"""
        try:
            if payment.id in self.payments:
                self.logger.warning(f"Payment with ID {payment.id} already exists")
                return False
            
            if payment.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {payment.receipt_id} not found")
                return False
            
            self.payments[payment.id] = payment
            self.logger.info(f"Payment added: {payment.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding payment: {str(e)}")
            return False
    
    def add_purchase_return(self, return_order: PurchaseReturn) -> bool:
        """Add purchase return"""
        try:
            if return_order.id in self.returns:
                self.logger.warning(f"Return with ID {return_order.id} already exists")
                return False
            
            if return_order.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {return_order.receipt_id} not found")
                return False
            
            if return_order.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {return_order.supplier_id} not found")
                return False
            
            self.returns[return_order.id] = return_order
            self.logger.info(f"Return added: {return_order.return_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding return: {str(e)}")
            return False
    
    def add_return_item(self, item: PurchaseReturnItem) -> bool:
        """Add return item"""
        try:
            if item.id in self.return_items:
                self.logger.warning(f"Return item with ID {item.id} already exists")
                return False
            
            if item.return_id not in self.returns:
                self.logger.error(f"Return {item.return_id} not found")
                return False
            
            if item.receipt_item_id not in self.receipt_items:
                self.logger.error(f"Receipt item {item.receipt_item_id} not found")
                return False
            
            self.return_items[item.id] = item
            self.logger.info(f"Return item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding return item: {str(e)}")
            return False
    
    def add_purchase_invoice(self, invoice: PurchaseInvoice) -> bool:
        """Add purchase invoice"""
        try:
            if invoice.id in self.invoices:
                self.logger.warning(f"Invoice with ID {invoice.id} already exists")
                return False
            
            if invoice.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {invoice.receipt_id} not found")
                return False
            
            if invoice.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {invoice.supplier_id} not found")
                return False
            
            self.invoices[invoice.id] = invoice
            self.logger.info(f"Invoice added: {invoice.invoice_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding invoice: {str(e)}")
            return False
    
    def add_purchase_analysis(self, analysis: PurchaseAnalysis) -> bool:
        """Add purchase analysis"""
        try:
            if analysis.id in self.analyses:
                self.logger.warning(f"Analysis with ID {analysis.id} already exists")
                return False
            
            if analysis.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {analysis.supplier_id} not found")
                return False
            
            self.analyses[analysis.id] = analysis
            self.logger.info(f"Analysis added: {analysis.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding analysis: {str(e)}")
            return False
    
    def calculate_supplier_performance(self, supplier_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calculate supplier performance metrics"""
        try:
            # Get supplier's orders for period
            period_orders = [
                order for order in self.orders.values()
                if order.supplier_id == supplier_id
                and start_date <= order.order_date <= end_date
            ]
            
            # Get supplier's receipts for period
            period_receipts = [
                receipt for receipt in self.receipts.values()
                if receipt.supplier_id == supplier_id
                and start_date <= receipt.receipt_date <= end_date
            ]
            
            # Calculate metrics
            metrics = {
                "total_orders": len(period_orders),
                "total_amount": sum(order.total_amount for order in period_orders),
                "currency": period_orders[0].currency if period_orders else None,
                "average_delivery_time": self.calculate_average_delivery_time(period_orders),
                "on_time_delivery_rate": self.calculate_on_time_delivery_rate(period_orders),
                "quality_rate": self.calculate_quality_rate(period_receipts),
                "payment_performance": self.calculate_payment_performance(supplier_id, start_date, end_date)
            }
            
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating supplier performance: {str(e)}")
            return {}
    
    def calculate_average_delivery_time(self, orders: List[PurchaseOrder]) -> int:
        """Calculate average delivery time in days"""
        try:
            delivery_times = []
            for order in orders:
                if order.status == PurchaseOrderStatus.RECEIVED:
                    receipt = next(
                        (r for r in self.receipts.values() if r.order_id == order.id),
                        None
                    )
                    if receipt:
                        delivery_time = (receipt.receipt_date - order.order_date).days
                        delivery_times.append(delivery_time)
            
            return int(np.mean(delivery_times)) if delivery_times else 0
        except Exception as e:
            self.logger.error(f"Error calculating average delivery time: {str(e)}")
            return 0
    
    def calculate_on_time_delivery_rate(self, orders: List[PurchaseOrder]) -> Decimal:
        """Calculate on-time delivery rate"""
        try:
            if not orders:
                return Decimal('0')
            
            on_time_deliveries = 0
            for order in orders:
                if order.status == PurchaseOrderStatus.RECEIVED:
                    receipt = next(
                        (r for r in self.receipts.values() if r.order_id == order.id),
                        None
                    )
                    if receipt and receipt.receipt_date <= order.delivery_date:
                        on_time_deliveries += 1
            
            return Decimal(str(on_time_deliveries / len(orders)))
        except Exception as e:
            self.logger.error(f"Error calculating on-time delivery rate: {str(e)}")
            return Decimal('0')
    
    def calculate_quality_rate(self, receipts: List[PurchaseReceipt]) -> Decimal:
        """Calculate quality rate based on returns"""
        try:
            if not receipts:
                return Decimal('1')
            
            total_items = sum(
                len([item for item in self.receipt_items.values() if item.receipt_id == receipt.id])
                for receipt in receipts
            )
            
            if total_items == 0:
                return Decimal('1')
            
            returned_items = sum(
                len([item for item in self.return_items.values() if item.receipt_id == receipt.id])
                for receipt in receipts
            )
            
            return Decimal(str(1 - (returned_items / total_items)))
        except Exception as e:
            self.logger.error(f"Error calculating quality rate: {str(e)}")
            return Decimal('0')
    
    def calculate_payment_performance(self, supplier_id: str, start_date: date, end_date: date) -> Decimal:
        """Calculate payment performance"""
        try:
            # Get supplier's invoices for period
            period_invoices = [
                invoice for invoice in self.invoices.values()
                if invoice.supplier_id == supplier_id
                and start_date <= invoice.invoice_date <= end_date
            ]
            
            if not period_invoices:
                return Decimal('1')
            
            # Calculate total amount and paid amount
            total_amount = sum(invoice.total_amount for invoice in period_invoices)
            paid_amount = sum(
                sum(payment.amount for payment in self.payments.values() if payment.receipt_id == invoice.receipt_id)
                for invoice in period_invoices
            )
            
            return Decimal(str(paid_amount / total_amount))
        except Exception as e:
            self.logger.error(f"Error calculating payment performance: {str(e)}")
            return Decimal('0')
    
    def generate_purchase_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate purchase report"""
        try:
            # Get orders for period
            period_orders = [
                order for order in self.orders.values()
                if start_date <= order.order_date <= end_date
            ]
            
            # Get receipts for period
            period_receipts = [
                receipt for receipt in self.receipts.values()
                if start_date <= receipt.receipt_date <= end_date
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
                    "by_supplier": self.calculate_orders_by_supplier(period_orders),
                    "by_type": self.calculate_orders_by_type(period_orders)
                },
                "receipts": {
                    "total": len(period_receipts),
                    "total_amount": sum(receipt.total_amount for receipt in period_receipts),
                    "by_supplier": self.calculate_receipts_by_supplier(period_receipts)
                },
                "returns": {
                    "total": len(period_returns),
                    "total_amount": sum(return_order.total_amount for return_order in period_returns),
                    "by_supplier": self.calculate_returns_by_supplier(period_returns)
                },
                "payments": {
                    "total": sum(payment.amount for payment in self.payments.values() if start_date <= payment.payment_date <= end_date),
                    "by_status": self.calculate_payments_by_status(start_date, end_date)
                },
                "supplier_performance": self.calculate_supplier_performance_metrics(start_date, end_date)
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating purchase report: {str(e)}")
            return {}
    
    def calculate_orders_by_status(self, orders: List[PurchaseOrder]) -> Dict[str, int]:
        """Calculate orders by status"""
        try:
            status_counts = {}
            for status in PurchaseOrderStatus:
                status_counts[status.value] = len([
                    order for order in orders
                    if order.status == status
                ])
            return status_counts
        except Exception as e:
            self.logger.error(f"Error calculating orders by status: {str(e)}")
            return {}
    
    def calculate_orders_by_supplier(self, orders: List[PurchaseOrder]) -> Dict[str, Dict[str, Any]]:
        """Calculate orders by supplier"""
        try:
            supplier_orders = {}
            for order in orders:
                if order.supplier_id not in supplier_orders:
                    supplier_orders[order.supplier_id] = {
                        "count": 0,
                        "total_amount": Decimal('0'),
                        "currency": order.currency
                    }
                supplier_orders[order.supplier_id]["count"] += 1
                supplier_orders[order.supplier_id]["total_amount"] += order.total_amount
            return supplier_orders
        except Exception as e:
            self.logger.error(f"Error calculating orders by supplier: {str(e)}")
            return {}
    
    def calculate_orders_by_type(self, orders: List[PurchaseOrder]) -> Dict[str, int]:
        """Calculate orders by type"""
        try:
            type_counts = {}
            for order_type in PurchaseOrderType:
                type_counts[order_type.value] = len([
                    order for order in orders
                    if order.type == order_type
                ])
            return type_counts
        except Exception as e:
            self.logger.error(f"Error calculating orders by type: {str(e)}")
            return {}
    
    def calculate_receipts_by_supplier(self, receipts: List[PurchaseReceipt]) -> Dict[str, Dict[str, Any]]:
        """Calculate receipts by supplier"""
        try:
            supplier_receipts = {}
            for receipt in receipts:
                if receipt.supplier_id not in supplier_receipts:
                    supplier_receipts[receipt.supplier_id] = {
                        "count": 0,
                        "total_amount": Decimal('0'),
                        "currency": receipt.currency
                    }
                supplier_receipts[receipt.supplier_id]["count"] += 1
                supplier_receipts[receipt.supplier_id]["total_amount"] += receipt.total_amount
            return supplier_receipts
        except Exception as e:
            self.logger.error(f"Error calculating receipts by supplier: {str(e)}")
            return {}
    
    def calculate_returns_by_supplier(self, returns: List[PurchaseReturn]) -> Dict[str, Dict[str, Any]]:
        """Calculate returns by supplier"""
        try:
            supplier_returns = {}
            for return_order in returns:
                if return_order.supplier_id not in supplier_returns:
                    supplier_returns[return_order.supplier_id] = {
                        "count": 0,
                        "total_amount": Decimal('0'),
                        "currency": return_order.currency
                    }
                supplier_returns[return_order.supplier_id]["count"] += 1
                supplier_returns[return_order.supplier_id]["total_amount"] += return_order.total_amount
            return supplier_returns
        except Exception as e:
            self.logger.error(f"Error calculating returns by supplier: {str(e)}")
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
    
    def calculate_supplier_performance_metrics(self, start_date: date, end_date: date) -> Dict[str, Dict[str, Any]]:
        """Calculate supplier performance metrics"""
        try:
            metrics = {}
            for supplier_id in self.suppliers:
                metrics[supplier_id] = self.calculate_supplier_performance(
                    supplier_id,
                    start_date,
                    end_date
                )
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating supplier performance metrics: {str(e)}")
            return {}
    
    def add_rfq(self, rfq: RFQ) -> bool:
        """Add new RFQ"""
        try:
            if rfq.id in self.rfqs:
                self.logger.warning(f"RFQ with ID {rfq.id} already exists")
                return False
            
            self.rfqs[rfq.id] = rfq
            self.logger.info(f"RFQ added: {rfq.number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding RFQ: {str(e)}")
            return False
    
    def add_rfq_item(self, item: RFQItem) -> bool:
        """Add RFQ item"""
        try:
            if item.id in self.rfq_items:
                self.logger.warning(f"RFQ item with ID {item.id} already exists")
                return False
            
            if item.rfq_id not in self.rfqs:
                self.logger.error(f"RFQ {item.rfq_id} not found")
                return False
            
            self.rfq_items[item.id] = item
            self.logger.info(f"RFQ item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding RFQ item: {str(e)}")
            return False
    
    def add_rfq_response(self, response: RFQResponse) -> bool:
        """Add RFQ response"""
        try:
            if response.id in self.rfq_responses:
                self.logger.warning(f"RFQ response with ID {response.id} already exists")
                return False
            
            if response.rfq_id not in self.rfqs:
                self.logger.error(f"RFQ {response.rfq_id} not found")
                return False
            
            if response.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {response.supplier_id} not found")
                return False
            
            self.rfq_responses[response.id] = response
            self.logger.info(f"RFQ response added: {response.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding RFQ response: {str(e)}")
            return False
    
    def add_rfq_response_item(self, item: RFQResponseItem) -> bool:
        """Add RFQ response item"""
        try:
            if item.id in self.rfq_response_items:
                self.logger.warning(f"RFQ response item with ID {item.id} already exists")
                return False
            
            if item.response_id not in self.rfq_responses:
                self.logger.error(f"RFQ response {item.response_id} not found")
                return False
            
            if item.rfq_item_id not in self.rfq_items:
                self.logger.error(f"RFQ item {item.rfq_item_id} not found")
                return False
            
            self.rfq_response_items[item.id] = item
            self.logger.info(f"RFQ response item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding RFQ response item: {str(e)}")
            return False
    
    def add_tender(self, tender: Tender) -> bool:
        """Add new tender"""
        try:
            if tender.id in self.tenders:
                self.logger.warning(f"Tender with ID {tender.id} already exists")
                return False
            
            self.tenders[tender.id] = tender
            self.logger.info(f"Tender added: {tender.number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tender: {str(e)}")
            return False
    
    def add_tender_item(self, item: TenderItem) -> bool:
        """Add tender item"""
        try:
            if item.id in self.tender_items:
                self.logger.warning(f"Tender item with ID {item.id} already exists")
                return False
            
            if item.tender_id not in self.tenders:
                self.logger.error(f"Tender {item.tender_id} not found")
                return False
            
            self.tender_items[item.id] = item
            self.logger.info(f"Tender item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tender item: {str(e)}")
            return False
    
    def add_tender_response(self, response: TenderResponse) -> bool:
        """Add tender response"""
        try:
            if response.id in self.tender_responses:
                self.logger.warning(f"Tender response with ID {response.id} already exists")
                return False
            
            if response.tender_id not in self.tenders:
                self.logger.error(f"Tender {response.tender_id} not found")
                return False
            
            if response.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {response.supplier_id} not found")
                return False
            
            self.tender_responses[response.id] = response
            self.logger.info(f"Tender response added: {response.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tender response: {str(e)}")
            return False
    
    def add_tender_response_item(self, item: TenderResponseItem) -> bool:
        """Add tender response item"""
        try:
            if item.id in self.tender_response_items:
                self.logger.warning(f"Tender response item with ID {item.id} already exists")
                return False
            
            if item.response_id not in self.tender_responses:
                self.logger.error(f"Tender response {item.response_id} not found")
                return False
            
            if item.tender_item_id not in self.tender_items:
                self.logger.error(f"Tender item {item.tender_item_id} not found")
                return False
            
            self.tender_response_items[item.id] = item
            self.logger.info(f"Tender response item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding tender response item: {str(e)}")
            return False
    
    def add_contract(self, contract: Contract) -> bool:
        """Add new contract"""
        try:
            if contract.id in self.contracts:
                self.logger.warning(f"Contract with ID {contract.id} already exists")
                return False
            
            if contract.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {contract.supplier_id} not found")
                return False
            
            self.contracts[contract.id] = contract
            self.logger.info(f"Contract added: {contract.number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding contract: {str(e)}")
            return False
    
    def add_contract_item(self, item: ContractItem) -> bool:
        """Add contract item"""
        try:
            if item.id in self.contract_items:
                self.logger.warning(f"Contract item with ID {item.id} already exists")
                return False
            
            if item.contract_id not in self.contracts:
                self.logger.error(f"Contract {item.contract_id} not found")
                return False
            
            self.contract_items[item.id] = item
            self.logger.info(f"Contract item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding contract item: {str(e)}")
            return False
    
    def add_quality_standard(self, standard: QualityStandard) -> bool:
        """Add quality standard"""
        try:
            if standard.id in self.quality_standards:
                self.logger.warning(f"Quality standard with ID {standard.id} already exists")
                return False
            
            self.quality_standards[standard.id] = standard
            self.logger.info(f"Quality standard added: {standard.code}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quality standard: {str(e)}")
            return False
    
    def add_quality_inspection(self, inspection: QualityInspection) -> bool:
        """Add quality inspection"""
        try:
            if inspection.id in self.quality_inspections:
                self.logger.warning(f"Quality inspection with ID {inspection.id} already exists")
                return False
            
            if inspection.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {inspection.receipt_id} not found")
                return False
            
            self.quality_inspections[inspection.id] = inspection
            self.logger.info(f"Quality inspection added: {inspection.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quality inspection: {str(e)}")
            return False
    
    def add_quality_inspection_item(self, item: QualityInspectionItem) -> bool:
        """Add quality inspection item"""
        try:
            if item.id in self.quality_inspection_items:
                self.logger.warning(f"Quality inspection item with ID {item.id} already exists")
                return False
            
            if item.inspection_id not in self.quality_inspections:
                self.logger.error(f"Quality inspection {item.inspection_id} not found")
                return False
            
            if item.receipt_item_id not in self.receipt_items:
                self.logger.error(f"Receipt item {item.receipt_item_id} not found")
                return False
            
            self.quality_inspection_items[item.id] = item
            self.logger.info(f"Quality inspection item added: {item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quality inspection item: {str(e)}")
            return False
    
    def add_quality_certificate(self, certificate: QualityCertificate) -> bool:
        """Add quality certificate"""
        try:
            if certificate.id in self.quality_certificates:
                self.logger.warning(f"Quality certificate with ID {certificate.id} already exists")
                return False
            
            if certificate.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {certificate.supplier_id} not found")
                return False
            
            if certificate.standard_id not in self.quality_standards:
                self.logger.error(f"Quality standard {certificate.standard_id} not found")
                return False
            
            self.quality_certificates[certificate.id] = certificate
            self.logger.info(f"Quality certificate added: {certificate.certificate_number}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding quality certificate: {str(e)}")
            return False
    
    def add_inventory_control(self, control: InventoryControl) -> bool:
        """Add inventory control"""
        try:
            if control.id in self.inventory_controls:
                self.logger.warning(f"Inventory control with ID {control.id} already exists")
                return False
            
            self.inventory_controls[control.id] = control
            self.logger.info(f"Inventory control added: {control.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding inventory control: {str(e)}")
            return False
    
    def add_cost(self, cost: Cost) -> bool:
        """Add cost"""
        try:
            if cost.id in self.costs:
                self.logger.warning(f"Cost with ID {cost.id} already exists")
                return False
            
            if cost.receipt_id not in self.receipts:
                self.logger.error(f"Receipt {cost.receipt_id} not found")
                return False
            
            self.costs[cost.id] = cost
            self.logger.info(f"Cost added: {cost.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding cost: {str(e)}")
            return False
    
    def add_risk(self, risk: Risk) -> bool:
        """Add risk"""
        try:
            if risk.id in self.risks:
                self.logger.warning(f"Risk with ID {risk.id} already exists")
                return False
            
            if risk.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {risk.supplier_id} not found")
                return False
            
            self.risks[risk.id] = risk
            self.logger.info(f"Risk added: {risk.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding risk: {str(e)}")
            return False
    
    def add_communication(self, communication: Communication) -> bool:
        """Add communication"""
        try:
            if communication.id in self.communications:
                self.logger.warning(f"Communication with ID {communication.id} already exists")
                return False
            
            if communication.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {communication.supplier_id} not found")
                return False
            
            self.communications[communication.id] = communication
            self.logger.info(f"Communication added: {communication.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding communication: {str(e)}")
            return False
    
    def add_document(self, document: Document) -> bool:
        """Add document"""
        try:
            if document.id in self.documents:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            if document.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {document.supplier_id} not found")
                return False
            
            self.documents[document.id] = document
            self.logger.info(f"Document added: {document.title}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            return False
    
    def add_budget(self, budget: Budget) -> bool:
        """Add budget"""
        try:
            if budget.id in self.budgets:
                self.logger.warning(f"Budget with ID {budget.id} already exists")
                return False
            
            self.budgets[budget.id] = budget
            self.logger.info(f"Budget added: {budget.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding budget: {str(e)}")
            return False
    
    def add_supplier_evaluation(self, evaluation: SupplierEvaluation) -> bool:
        """Add supplier evaluation"""
        try:
            if evaluation.id in self.supplier_evaluations:
                self.logger.warning(f"Supplier evaluation with ID {evaluation.id} already exists")
                return False
            
            if evaluation.supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {evaluation.supplier_id} not found")
                return False
            
            self.supplier_evaluations[evaluation.id] = evaluation
            self.logger.info(f"Supplier evaluation added: {evaluation.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding supplier evaluation: {str(e)}")
            return False
    
    def evaluate_rfq_responses(self, rfq_id: str) -> Dict[str, Any]:
        """Evaluate RFQ responses"""
        try:
            rfq = self.rfqs.get(rfq_id)
            if not rfq:
                self.logger.error(f"RFQ {rfq_id} not found")
                return {}
            
            responses = [
                response for response in self.rfq_responses.values()
                if response.rfq_id == rfq_id
            ]
            
            if not responses:
                return {"message": "No responses found"}
            
            # Sort responses by total amount
            sorted_responses = sorted(responses, key=lambda x: x.total_amount)
            
            return {
                "rfq_id": rfq_id,
                "total_responses": len(responses),
                "lowest_amount": sorted_responses[0].total_amount,
                "highest_amount": sorted_responses[-1].total_amount,
                "average_amount": sum(r.total_amount for r in responses) / len(responses),
                "responses": [
                    {
                        "supplier_id": r.supplier_id,
                        "total_amount": r.total_amount,
                        "delivery_terms": r.delivery_terms,
                        "payment_terms": r.payment_terms,
                        "validity_period": r.validity_period
                    }
                    for r in sorted_responses
                ]
            }
        except Exception as e:
            self.logger.error(f"Error evaluating RFQ responses: {str(e)}")
            return {}
    
    def evaluate_tender_responses(self, tender_id: str) -> Dict[str, Any]:
        """Evaluate tender responses"""
        try:
            tender = self.tenders.get(tender_id)
            if not tender:
                self.logger.error(f"Tender {tender_id} not found")
                return {}
            
            responses = [
                response for response in self.tender_responses.values()
                if response.tender_id == tender_id
            ]
            
            if not responses:
                return {"message": "No responses found"}
            
            # Sort responses by total score
            sorted_responses = sorted(responses, key=lambda x: x.total_score, reverse=True)
            
            return {
                "tender_id": tender_id,
                "total_responses": len(responses),
                "highest_score": sorted_responses[0].total_score,
                "lowest_score": sorted_responses[-1].total_score,
                "average_score": sum(r.total_score for r in responses) / len(responses),
                "responses": [
                    {
                        "supplier_id": r.supplier_id,
                        "technical_score": r.technical_score,
                        "financial_score": r.financial_score,
                        "total_score": r.total_score,
                        "total_amount": r.total_amount
                    }
                    for r in sorted_responses
                ]
            }
        except Exception as e:
            self.logger.error(f"Error evaluating tender responses: {str(e)}")
            return {}
    
    def calculate_supplier_risk_score(self, supplier_id: str) -> Dict[str, Any]:
        """Calculate supplier risk score"""
        try:
            if supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {supplier_id} not found")
                return {}
            
            risks = [
                risk for risk in self.risks.values()
                if risk.supplier_id == supplier_id
            ]
            
            if not risks:
                return {"message": "No risks found"}
            
            # Calculate risk score based on level and probability
            risk_scores = {
                RiskLevel.LOW: 1,
                RiskLevel.MEDIUM: 2,
                RiskLevel.HIGH: 3,
                RiskLevel.CRITICAL: 4
            }
            
            total_score = sum(risk_scores[risk.level] for risk in risks)
            average_score = total_score / len(risks)
            
            return {
                "supplier_id": supplier_id,
                "total_risks": len(risks),
                "risk_score": average_score,
                "risks": [
                    {
                        "type": risk.risk_type,
                        "level": risk.level.value,
                        "impact": risk.impact,
                        "probability": risk.probability,
                        "mitigation": risk.mitigation
                    }
                    for risk in risks
                ]
            }
        except Exception as e:
            self.logger.error(f"Error calculating supplier risk score: {str(e)}")
            return {}
    
    def calculate_supplier_performance_score(self, supplier_id: str) -> Dict[str, Any]:
        """Calculate supplier performance score"""
        try:
            if supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {supplier_id} not found")
                return {}
            
            evaluations = [
                evaluation for evaluation in self.supplier_evaluations.values()
                if evaluation.supplier_id == supplier_id
            ]
            
            if not evaluations:
                return {"message": "No evaluations found"}
            
            # Calculate average score
            total_score = sum(evaluation.total_score for evaluation in evaluations)
            average_score = total_score / len(evaluations)
            
            return {
                "supplier_id": supplier_id,
                "total_evaluations": len(evaluations),
                "average_score": average_score,
                "evaluations": [
                    {
                        "date": evaluation.evaluation_date.isoformat(),
                        "criteria": evaluation.criteria,
                        "total_score": evaluation.total_score
                    }
                    for evaluation in evaluations
                ]
            }
        except Exception as e:
            self.logger.error(f"Error calculating supplier performance score: {str(e)}")
            return {}
    
    def generate_supplier_report(self, supplier_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Generate supplier report"""
        try:
            if supplier_id not in self.suppliers:
                self.logger.error(f"Supplier {supplier_id} not found")
                return {}
            
            # Get supplier's orders for period
            period_orders = [
                order for order in self.orders.values()
                if order.supplier_id == supplier_id
                and start_date <= order.order_date <= end_date
            ]
            
            # Get supplier's receipts for period
            period_receipts = [
                receipt for receipt in self.receipts.values()
                if receipt.supplier_id == supplier_id
                and start_date <= receipt.receipt_date <= end_date
            ]
            
            # Get supplier's returns for period
            period_returns = [
                return_order for return_order in self.returns.values()
                if return_order.supplier_id == supplier_id
                and start_date <= return_order.return_date <= end_date
            ]
            
            # Get supplier's payments for period
            period_payments = [
                payment for payment in self.payments.values()
                if payment.receipt_id in [r.id for r in period_receipts]
            ]
            
            # Calculate metrics
            report = {
                "supplier_id": supplier_id,
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "orders": {
                    "total": len(period_orders),
                    "total_amount": sum(order.total_amount for order in period_orders),
                    "by_status": self.calculate_orders_by_status(period_orders)
                },
                "receipts": {
                    "total": len(period_receipts),
                    "total_amount": sum(receipt.total_amount for receipt in period_receipts)
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
                    "delivery_time": self.calculate_average_delivery_time(period_orders),
                    "on_time_delivery": self.calculate_on_time_delivery_rate(period_orders),
                    "quality_rate": self.calculate_quality_rate(period_receipts),
                    "payment_performance": self.calculate_payment_performance(supplier_id, start_date, end_date)
                },
                "risk_score": self.calculate_supplier_risk_score(supplier_id),
                "performance_score": self.calculate_supplier_performance_score(supplier_id)
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating supplier report: {str(e)}")
            return {} 