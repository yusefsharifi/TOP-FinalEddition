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
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import qrcode
import numpy as np
from datetime import datetime, timedelta

class ItemType(Enum):
    RAW_MATERIAL = "raw_material"
    FINISHED_GOOD = "finished_good"
    SPARE_PART = "spare_part"
    TOOL = "tool"
    EQUIPMENT = "equipment"
    CONSUMABLE = "consumable"

class LocationType(Enum):
    WAREHOUSE = "warehouse"
    STORAGE_ROOM = "storage_room"
    PRODUCTION_LINE = "production_line"
    OFFICE = "office"
    VEHICLE = "vehicle"
    EXTERNAL = "external"

class MovementType(Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER = "transfer"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    SCRAP = "scrap"

class StockStatus(Enum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    IN_TRANSIT = "in_transit"
    DAMAGED = "damaged"
    EXPIRED = "expired"
    SCRAPPED = "scrapped"

@dataclass
class Item:
    id: str
    code: str
    name: str
    type: ItemType
    description: str
    unit: str
    min_quantity: Decimal
    max_quantity: Decimal
    reorder_point: Decimal
    unit_price: Decimal
    currency: str
    category: str
    specifications: Dict[str, Any]
    is_active: bool = True
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Location:
    id: str
    code: str
    name: str
    type: LocationType
    parent_id: Optional[str]
    capacity: Decimal
    current_quantity: Decimal
    address: str
    contact_person: str
    contact_phone: str
    is_active: bool = True
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Stock:
    id: str
    item_id: str
    location_id: str
    quantity: Decimal
    status: StockStatus
    batch_number: Optional[str]
    expiry_date: Optional[date]
    unit_price: Decimal
    currency: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Movement:
    id: str
    type: MovementType
    item_id: str
    from_location_id: Optional[str]
    to_location_id: Optional[str]
    quantity: Decimal
    unit_price: Decimal
    currency: str
    reference_number: str
    reference_date: date
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class InventoryCount:
    id: str
    location_id: str
    count_date: date
    status: str
    counted_by: str
    verified_by: Optional[str]
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class InventoryCountItem:
    id: str
    count_id: str
    item_id: str
    expected_quantity: Decimal
    counted_quantity: Decimal
    difference: Decimal
    notes: str
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class InventoryReport:
    id: str
    name: str
    description: str
    period_start: date
    period_end: date
    content: Dict[str, Any]
    created_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class InventoryManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items: Dict[str, Item] = {}
        self.locations: Dict[str, Location] = {}
        self.stocks: Dict[str, Stock] = {}
        self.movements: Dict[str, Movement] = {}
        self.counts: Dict[str, InventoryCount] = {}
        self.count_items: Dict[str, InventoryCountItem] = {}
        self.reports: Dict[str, InventoryReport] = {}
        
        # Create necessary directories
        self.create_directories()
        
        # Load items from file
        self.load_items()
        
        # Initialize barcode and QR code generators
        self.barcode_writer = ImageWriter()
        self.qr_generator = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
    
    def create_directories(self):
        """Create necessary directories for inventory management"""
        try:
            # Create inventory data directory
            data_dir = os.path.join(os.path.dirname(__file__), 'inventory_data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Create inventory reports directory
            reports_dir = os.path.join(os.path.dirname(__file__), 'inventory_reports')
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir)
            
            # Create barcode images directory
            barcode_dir = os.path.join(os.path.dirname(__file__), 'barcode_images')
            if not os.path.exists(barcode_dir):
                os.makedirs(barcode_dir)
            
            self.logger.info("Inventory management directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {str(e)}")
    
    def load_items(self):
        """Load items from JSON file"""
        try:
            items_file = os.path.join(os.path.dirname(__file__), 'items.json')
            if os.path.exists(items_file):
                with open(items_file, 'r', encoding='utf-8') as f:
                    items_data = json.load(f)
                    for item_data in items_data:
                        item = Item(
                            id=item_data['id'],
                            code=item_data['code'],
                            name=item_data['name'],
                            type=ItemType(item_data['type']),
                            description=item_data['description'],
                            unit=item_data['unit'],
                            min_quantity=Decimal(str(item_data['min_quantity'])),
                            max_quantity=Decimal(str(item_data['max_quantity'])),
                            reorder_point=Decimal(str(item_data['reorder_point'])),
                            unit_price=Decimal(str(item_data['unit_price'])),
                            currency=item_data['currency'],
                            category=item_data['category'],
                            specifications=item_data['specifications'],
                            is_active=item_data['is_active'],
                            created_by=item_data['created_by']
                        )
                        self.items[item.id] = item
                self.logger.info("Items loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading items: {str(e)}")
    
    def add_item(self, item: Item) -> bool:
        """Add new item"""
        try:
            if item.id in self.items:
                self.logger.warning(f"Item with ID {item.id} already exists")
                return False
            
            self.items[item.id] = item
            self.logger.info(f"Item added: {item.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding item: {str(e)}")
            return False
    
    def update_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update item details"""
        try:
            item = self.items.get(item_id)
            if not item:
                self.logger.error(f"Item {item_id} not found")
                return False
            
            # Update item attributes
            for key, value in updates.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            item.updated_at = datetime.now()
            self.logger.info(f"Item updated: {item.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating item: {str(e)}")
            return False
    
    def generate_barcode(self, item: Item) -> Optional[str]:
        """Generate barcode for item"""
        try:
            # Generate Code128 barcode
            code128 = barcode.get('code128', item.code, writer=self.barcode_writer)
            
            # Save barcode image
            barcode_path = os.path.join(os.path.dirname(__file__), 
                                      'barcode_images', 
                                      f'{item.code}.png')
            code128.save(barcode_path)
            
            return barcode_path
        except Exception as e:
            self.logger.error(f"Error generating barcode: {str(e)}")
            return None
    
    def generate_qr_code(self, item: Item) -> Optional[str]:
        """Generate QR code for item"""
        try:
            # Generate QR code data
            qr_data = {
                "id": item.id,
                "code": item.code,
                "name": item.name,
                "type": item.type.value,
                "unit": item.unit,
                "unit_price": str(item.unit_price),
                "currency": item.currency
            }
            
            # Generate QR code
            self.qr_generator.clear()
            self.qr_generator.add_data(json.dumps(qr_data))
            self.qr_generator.make(fit=True)
            
            # Create QR code image
            qr_image = self.qr_generator.make_image(fill_color="black", back_color="white")
            
            # Save QR code image
            qr_path = os.path.join(os.path.dirname(__file__), 
                                 'barcode_images', 
                                 f'{item.code}_qr.png')
            qr_image.save(qr_path)
            
            return qr_path
        except Exception as e:
            self.logger.error(f"Error generating QR code: {str(e)}")
            return None
    
    def add_location(self, location: Location) -> bool:
        """Add new location"""
        try:
            if location.id in self.locations:
                self.logger.warning(f"Location with ID {location.id} already exists")
                return False
            
            if location.parent_id and location.parent_id not in self.locations:
                self.logger.error(f"Parent location {location.parent_id} not found")
                return False
            
            self.locations[location.id] = location
            self.logger.info(f"Location added: {location.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding location: {str(e)}")
            return False
    
    def update_location(self, location_id: str, updates: Dict[str, Any]) -> bool:
        """Update location details"""
        try:
            location = self.locations.get(location_id)
            if not location:
                self.logger.error(f"Location {location_id} not found")
                return False
            
            # Update location attributes
            for key, value in updates.items():
                if hasattr(location, key):
                    setattr(location, key, value)
            
            location.updated_at = datetime.now()
            self.logger.info(f"Location updated: {location.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating location: {str(e)}")
            return False
    
    def add_stock(self, stock: Stock) -> bool:
        """Add stock"""
        try:
            if stock.id in self.stocks:
                self.logger.warning(f"Stock with ID {stock.id} already exists")
                return False
            
            if stock.item_id not in self.items:
                self.logger.error(f"Item {stock.item_id} not found")
                return False
            
            if stock.location_id not in self.locations:
                self.logger.error(f"Location {stock.location_id} not found")
                return False
            
            self.stocks[stock.id] = stock
            self.logger.info(f"Stock added: {stock.item_id} at {stock.location_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding stock: {str(e)}")
            return False
    
    def update_stock(self, stock_id: str, updates: Dict[str, Any]) -> bool:
        """Update stock"""
        try:
            stock = self.stocks.get(stock_id)
            if not stock:
                self.logger.error(f"Stock {stock_id} not found")
                return False
            
            # Update stock attributes
            for key, value in updates.items():
                if hasattr(stock, key):
                    setattr(stock, key, value)
            
            stock.updated_at = datetime.now()
            self.logger.info(f"Stock updated: {stock.item_id} at {stock.location_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error updating stock: {str(e)}")
            return False
    
    def add_movement(self, movement: Movement) -> bool:
        """Add movement"""
        try:
            if movement.id in self.movements:
                self.logger.warning(f"Movement with ID {movement.id} already exists")
                return False
            
            if movement.item_id not in self.items:
                self.logger.error(f"Item {movement.item_id} not found")
                return False
            
            if movement.from_location_id and movement.from_location_id not in self.locations:
                self.logger.error(f"From location {movement.from_location_id} not found")
                return False
            
            if movement.to_location_id and movement.to_location_id not in self.locations:
                self.logger.error(f"To location {movement.to_location_id} not found")
                return False
            
            # Update stock quantities
            if movement.type == MovementType.RECEIPT:
                self.update_stock_quantity(movement.item_id, movement.to_location_id, movement.quantity)
            elif movement.type == MovementType.ISSUE:
                self.update_stock_quantity(movement.item_id, movement.from_location_id, -movement.quantity)
            elif movement.type == MovementType.TRANSFER:
                self.update_stock_quantity(movement.item_id, movement.from_location_id, -movement.quantity)
                self.update_stock_quantity(movement.item_id, movement.to_location_id, movement.quantity)
            
            self.movements[movement.id] = movement
            self.logger.info(f"Movement added: {movement.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding movement: {str(e)}")
            return False
    
    def update_stock_quantity(self, item_id: str, location_id: str, quantity_change: Decimal) -> bool:
        """Update stock quantity"""
        try:
            # Find existing stock
            stock = next(
                (s for s in self.stocks.values() 
                 if s.item_id == item_id and s.location_id == location_id),
                None
            )
            
            if stock:
                # Update existing stock
                stock.quantity += quantity_change
                stock.updated_at = datetime.now()
            else:
                # Create new stock
                stock = Stock(
                    id=str(uuid.uuid4()),
                    item_id=item_id,
                    location_id=location_id,
                    quantity=quantity_change,
                    status=StockStatus.AVAILABLE,
                    batch_number=None,
                    expiry_date=None,
                    unit_price=self.items[item_id].unit_price,
                    currency=self.items[item_id].currency,
                    created_by="system"
                )
                self.stocks[stock.id] = stock
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating stock quantity: {str(e)}")
            return False
    
    def add_inventory_count(self, count: InventoryCount) -> bool:
        """Add inventory count"""
        try:
            if count.id in self.counts:
                self.logger.warning(f"Count with ID {count.id} already exists")
                return False
            
            if count.location_id not in self.locations:
                self.logger.error(f"Location {count.location_id} not found")
                return False
            
            self.counts[count.id] = count
            self.logger.info(f"Count added: {count.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding count: {str(e)}")
            return False
    
    def add_count_item(self, count_item: InventoryCountItem) -> bool:
        """Add count item"""
        try:
            if count_item.id in self.count_items:
                self.logger.warning(f"Count item with ID {count_item.id} already exists")
                return False
            
            if count_item.count_id not in self.counts:
                self.logger.error(f"Count {count_item.count_id} not found")
                return False
            
            if count_item.item_id not in self.items:
                self.logger.error(f"Item {count_item.item_id} not found")
                return False
            
            self.count_items[count_item.id] = count_item
            self.logger.info(f"Count item added: {count_item.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding count item: {str(e)}")
            return False
    
    def generate_inventory_report(self, report: InventoryReport) -> bool:
        """Generate inventory report"""
        try:
            # Get movements for period
            period_movements = [
                m for m in self.movements.values()
                if report.period_start <= m.reference_date <= report.period_end
            ]
            
            # Calculate report metrics
            report.content = {
                "period": {
                    "start": report.period_start.isoformat(),
                    "end": report.period_end.isoformat()
                },
                "movements": {
                    "total": len(period_movements),
                    "by_type": self.calculate_movements_by_type(period_movements),
                    "by_item": self.calculate_movements_by_item(period_movements),
                    "by_location": self.calculate_movements_by_location(period_movements)
                },
                "stock": {
                    "by_location": self.get_stock_by_location(),
                    "by_item": self.get_stock_by_item(),
                    "low_stock": self.get_low_stock_items()
                },
                "value": {
                    "total": self.calculate_total_stock_value(),
                    "by_location": self.calculate_stock_value_by_location(),
                    "by_item": self.calculate_stock_value_by_item()
                }
            }
            
            # Save report
            report_file = os.path.join(os.path.dirname(__file__), 
                                     'inventory_reports', 
                                     f'report_{report.id}.json')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.content, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Error generating inventory report: {str(e)}")
            return False
    
    def calculate_movements_by_type(self, movements: List[Movement]) -> Dict[str, Any]:
        """Calculate movement metrics by type"""
        try:
            metrics = {}
            for movement_type in MovementType:
                type_movements = [m for m in movements if m.type == movement_type]
                metrics[movement_type.value] = {
                    "count": len(type_movements),
                    "total_quantity": sum(m.quantity for m in type_movements),
                    "total_value": sum(m.quantity * m.unit_price for m in type_movements)
                }
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating movements by type: {str(e)}")
            return {}
    
    def calculate_movements_by_item(self, movements: List[Movement]) -> Dict[str, Any]:
        """Calculate movement metrics by item"""
        try:
            metrics = {}
            for item_id in set(m.item_id for m in movements):
                item_movements = [m for m in movements if m.item_id == item_id]
                metrics[item_id] = {
                    "count": len(item_movements),
                    "total_quantity": sum(m.quantity for m in item_movements),
                    "total_value": sum(m.quantity * m.unit_price for m in item_movements)
                }
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating movements by item: {str(e)}")
            return {}
    
    def calculate_movements_by_location(self, movements: List[Movement]) -> Dict[str, Any]:
        """Calculate movement metrics by location"""
        try:
            metrics = {}
            for location_id in set(m.from_location_id for m in movements if m.from_location_id) | \
                          set(m.to_location_id for m in movements if m.to_location_id):
                location_movements = [
                    m for m in movements
                    if m.from_location_id == location_id or m.to_location_id == location_id
                ]
                metrics[location_id] = {
                    "count": len(location_movements),
                    "total_quantity": sum(m.quantity for m in location_movements),
                    "total_value": sum(m.quantity * m.unit_price for m in location_movements)
                }
            return metrics
        except Exception as e:
            self.logger.error(f"Error calculating movements by location: {str(e)}")
            return {}
    
    def get_stock_by_location(self) -> Dict[str, Any]:
        """Get stock summary by location"""
        try:
            summary = {}
            for location_id in self.locations:
                location_stocks = [
                    s for s in self.stocks.values()
                    if s.location_id == location_id
                ]
                if location_stocks:
                    summary[location_id] = {
                        "item_count": len(location_stocks),
                        "total_quantity": sum(s.quantity for s in location_stocks),
                        "total_value": sum(s.quantity * s.unit_price for s in location_stocks)
                    }
            return summary
        except Exception as e:
            self.logger.error(f"Error getting stock by location: {str(e)}")
            return {}
    
    def get_stock_by_item(self) -> Dict[str, Any]:
        """Get stock summary by item"""
        try:
            summary = {}
            for item_id in self.items:
                item_stocks = [
                    s for s in self.stocks.values()
                    if s.item_id == item_id
                ]
                if item_stocks:
                    summary[item_id] = {
                        "location_count": len(item_stocks),
                        "total_quantity": sum(s.quantity for s in item_stocks),
                        "total_value": sum(s.quantity * s.unit_price for s in item_stocks)
                    }
            return summary
        except Exception as e:
            self.logger.error(f"Error getting stock by item: {str(e)}")
            return {}
    
    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        """Get items with low stock"""
        try:
            low_stock = []
            for item_id, item in self.items.items():
                item_stocks = [
                    s for s in self.stocks.values()
                    if s.item_id == item_id
                ]
                total_quantity = sum(s.quantity for s in item_stocks)
                if total_quantity <= item.reorder_point:
                    low_stock.append({
                        "item_id": item_id,
                        "item_name": item.name,
                        "current_quantity": total_quantity,
                        "reorder_point": item.reorder_point,
                        "unit": item.unit
                    })
            return low_stock
        except Exception as e:
            self.logger.error(f"Error getting low stock items: {str(e)}")
            return []
    
    def calculate_total_stock_value(self) -> Decimal:
        """Calculate total stock value"""
        try:
            return sum(s.quantity * s.unit_price for s in self.stocks.values())
        except Exception as e:
            self.logger.error(f"Error calculating total stock value: {str(e)}")
            return Decimal('0')
    
    def calculate_stock_value_by_location(self) -> Dict[str, Decimal]:
        """Calculate stock value by location"""
        try:
            values = {}
            for location_id in self.locations:
                location_stocks = [
                    s for s in self.stocks.values()
                    if s.location_id == location_id
                ]
                if location_stocks:
                    values[location_id] = sum(s.quantity * s.unit_price for s in location_stocks)
            return values
        except Exception as e:
            self.logger.error(f"Error calculating stock value by location: {str(e)}")
            return {}
    
    def calculate_stock_value_by_item(self) -> Dict[str, Decimal]:
        """Calculate stock value by item"""
        try:
            values = {}
            for item_id in self.items:
                item_stocks = [
                    s for s in self.stocks.values()
                    if s.item_id == item_id
                ]
                if item_stocks:
                    values[item_id] = sum(s.quantity * s.unit_price for s in item_stocks)
            return values
        except Exception as e:
            self.logger.error(f"Error calculating stock value by item: {str(e)}")
            return {} 