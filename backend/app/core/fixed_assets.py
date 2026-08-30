from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

class AssetType(Enum):
    LAND = "land"
    BUILDING = "building"
    MACHINERY = "machinery"
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"
    FURNITURE = "furniture"
    COMPUTER = "computer"
    SOFTWARE = "software"
    OTHER = "other"

class AssetStatus(Enum):
    NEW = "new"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    IDLE = "idle"
    SOLD = "sold"
    SCRAPPED = "scrapped"

class DepreciationMethod(Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    SUM_OF_YEARS = "sum_of_years"
    UNITS_OF_PRODUCTION = "units_of_production"

class InsuranceType(Enum):
    FIRE = "fire"
    THEFT = "theft"
    NATURAL_DISASTER = "natural_disaster"
    LIABILITY = "liability"
    TRANSPORT = "transport"
    OTHER = "other"

class DocumentType(Enum):
    INVOICE = "invoice"
    OWNERSHIP = "ownership"
    CERTIFICATE = "certificate"
    MAINTENANCE = "maintenance"
    INSURANCE = "insurance"
    OTHER = "other"

@dataclass
class Asset:
    id: str
    code: str
    name: str
    type: AssetType
    description: str
    purchase_date: date
    purchase_price: Decimal
    salvage_value: Decimal
    useful_life: int  # در سال
    depreciation_method: DepreciationMethod
    location: str
    department_id: str
    status: AssetStatus = AssetStatus.NEW
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AssetComponent:
    id: str
    asset_id: str
    name: str
    description: str
    purchase_date: date
    purchase_price: Decimal
    salvage_value: Decimal
    useful_life: int
    depreciation_method: DepreciationMethod
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Maintenance:
    id: str
    asset_id: str
    type: str  # preventive, corrective, inspection
    description: str
    start_date: date
    end_date: Optional[date] = None
    cost: Decimal = Decimal('0')
    performed_by: str = ""
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Depreciation:
    id: str
    asset_id: str
    period_start: date
    period_end: date
    amount: Decimal
    accumulated_amount: Decimal
    book_value: Decimal
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AssetTransfer:
    id: str
    asset_id: str
    from_location: str
    to_location: str
    from_department: str
    to_department: str
    transfer_date: date
    reason: str
    approved_by: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class Insurance:
    id: str
    asset_id: str
    type: InsuranceType
    insurance_company: str
    policy_number: str
    start_date: date
    end_date: date
    coverage_amount: Decimal
    premium_amount: Decimal
    deductible: Decimal
    description: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class InsuranceClaim:
    id: str
    insurance_id: str
    claim_number: str
    incident_date: date
    description: str
    claim_amount: Decimal
    status: str  # pending, approved, rejected, paid
    payment_date: Optional[date] = None
    payment_amount: Decimal = Decimal('0')
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class AssetDocument:
    id: str
    asset_id: str
    type: DocumentType
    title: str
    description: str
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    upload_date: datetime
    uploaded_by: str
    is_active: bool = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class FixedAssetManager:
    def __init__(self, accounting_system):
        self.logger = logging.getLogger(__name__)
        self.accounting_system = accounting_system
        self.assets: Dict[str, Asset] = {}
        self.components: Dict[str, List[AssetComponent]] = {}
        self.maintenance: Dict[str, List[Maintenance]] = {}
        self.depreciation: Dict[str, List[Depreciation]] = {}
        self.transfers: Dict[str, List[AssetTransfer]] = {}
        self.insurance: Dict[str, List[Insurance]] = {}
        self.claims: Dict[str, List[InsuranceClaim]] = {}
        self.documents: Dict[str, List[AssetDocument]] = {}
        self.document_base_path = "documents/assets"
        
        # Create document directory if not exists
        if not os.path.exists(self.document_base_path):
            os.makedirs(self.document_base_path)
    
    def add_asset(self, asset: Asset) -> bool:
        """Add new asset"""
        try:
            if asset.id in self.assets:
                self.logger.warning(f"Asset with ID {asset.id} already exists")
                return False
            
            self.assets[asset.id] = asset
            self.components[asset.id] = []
            self.maintenance[asset.id] = []
            self.depreciation[asset.id] = []
            self.transfers[asset.id] = []
            
            self.logger.info(f"Asset {asset.name} added successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error adding asset: {str(e)}")
            return False
    
    def add_component(self, component: AssetComponent) -> bool:
        """Add component to asset"""
        try:
            if component.asset_id not in self.assets:
                self.logger.error(f"Asset {component.asset_id} not found")
                return False
            
            if component.id in [c.id for c in self.components[component.asset_id]]:
                self.logger.warning(f"Component with ID {component.id} already exists")
                return False
            
            self.components[component.asset_id].append(component)
            self.logger.info(f"Component added to asset {component.asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding component: {str(e)}")
            return False
    
    def schedule_maintenance(self, maintenance: Maintenance) -> bool:
        """Schedule maintenance for asset"""
        try:
            if maintenance.asset_id not in self.assets:
                self.logger.error(f"Asset {maintenance.asset_id} not found")
                return False
            
            if maintenance.id in [m.id for m in self.maintenance[maintenance.asset_id]]:
                self.logger.warning(f"Maintenance with ID {maintenance.id} already exists")
                return False
            
            self.maintenance[maintenance.asset_id].append(maintenance)
            self.logger.info(f"Maintenance scheduled for asset {maintenance.asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error scheduling maintenance: {str(e)}")
            return False
    
    def complete_maintenance(self, maintenance_id: str, asset_id: str, end_date: date, cost: Decimal) -> bool:
        """Complete maintenance"""
        try:
            maintenance = next((m for m in self.maintenance[asset_id] if m.id == maintenance_id), None)
            if not maintenance:
                return False
            
            if maintenance.status != "scheduled":
                self.logger.warning(f"Maintenance {maintenance_id} is not scheduled")
                return False
            
            maintenance.status = "completed"
            maintenance.end_date = end_date
            maintenance.cost = cost
            maintenance.updated_at = datetime.now()
            
            self.logger.info(f"Maintenance {maintenance_id} completed")
            return True
        except Exception as e:
            self.logger.error(f"Error completing maintenance: {str(e)}")
            return False
    
    def calculate_depreciation(self, asset_id: str, period_start: date, period_end: date) -> bool:
        """Calculate depreciation for asset"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return False
            
            if asset.status not in [AssetStatus.IN_USE, AssetStatus.MAINTENANCE]:
                self.logger.warning(f"Asset {asset_id} is not in use")
                return False
            
            # Get previous depreciation
            previous_depreciation = next(
                (d for d in reversed(self.depreciation[asset_id]) 
                 if d.period_end <= period_start),
                None
            )
            
            # Calculate depreciation amount
            depreciation_amount = self._calculate_depreciation_amount(
                asset,
                period_start,
                period_end,
                previous_depreciation.accumulated_amount if previous_depreciation else Decimal('0')
            )
            
            # Create depreciation record
            accumulated_amount = (previous_depreciation.accumulated_amount if previous_depreciation else Decimal('0')) + depreciation_amount
            book_value = asset.purchase_price - accumulated_amount
            
            depreciation = Depreciation(
                id=f"DEP_{asset_id}_{period_end.strftime('%Y%m')}",
                asset_id=asset_id,
                period_start=period_start,
                period_end=period_end,
                amount=depreciation_amount,
                accumulated_amount=accumulated_amount,
                book_value=book_value
            )
            
            self.depreciation[asset_id].append(depreciation)
            self.logger.info(f"Depreciation calculated for asset {asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error calculating depreciation: {str(e)}")
            return False
    
    def _calculate_depreciation_amount(self, asset: Asset, period_start: date, period_end: date, 
                                    accumulated_amount: Decimal) -> Decimal:
        """Calculate depreciation amount based on method"""
        try:
            if asset.depreciation_method == DepreciationMethod.STRAIGHT_LINE:
                annual_depreciation = (asset.purchase_price - asset.salvage_value) / Decimal(str(asset.useful_life))
                days_in_period = (period_end - period_start).days
                return annual_depreciation * Decimal(str(days_in_period)) / Decimal('365')
            
            elif asset.depreciation_method == DepreciationMethod.DECLINING_BALANCE:
                book_value = asset.purchase_price - accumulated_amount
                if book_value <= asset.salvage_value:
                    return Decimal('0')
                
                annual_rate = Decimal('2') / Decimal(str(asset.useful_life))  # Double declining balance
                days_in_period = (period_end - period_start).days
                return book_value * annual_rate * Decimal(str(days_in_period)) / Decimal('365')
            
            elif asset.depreciation_method == DepreciationMethod.SUM_OF_YEARS:
                remaining_life = asset.useful_life - (accumulated_amount / 
                    ((asset.purchase_price - asset.salvage_value) / Decimal(str(asset.useful_life))))
                if remaining_life <= 0:
                    return Decimal('0')
                
                sum_of_years = Decimal(str(asset.useful_life * (asset.useful_life + 1) / 2))
                annual_depreciation = (asset.purchase_price - asset.salvage_value) * remaining_life / sum_of_years
                days_in_period = (period_end - period_start).days
                return annual_depreciation * Decimal(str(days_in_period)) / Decimal('365')
            
            else:  # Units of Production
                # This method requires actual usage data
                return Decimal('0')
            
        except Exception as e:
            self.logger.error(f"Error calculating depreciation amount: {str(e)}")
            return Decimal('0')
    
    def transfer_asset(self, transfer: AssetTransfer) -> bool:
        """Transfer asset to new location/department"""
        try:
            if transfer.asset_id not in self.assets:
                self.logger.error(f"Asset {transfer.asset_id} not found")
                return False
            
            asset = self.assets[transfer.asset_id]
            if asset.status != AssetStatus.IN_USE:
                self.logger.warning(f"Asset {transfer.asset_id} is not in use")
                return False
            
            # Update asset location and department
            asset.location = transfer.to_location
            asset.department_id = transfer.to_department
            asset.updated_at = datetime.now()
            
            # Record transfer
            self.transfers[transfer.asset_id].append(transfer)
            self.logger.info(f"Asset {transfer.asset_id} transferred")
            return True
        except Exception as e:
            self.logger.error(f"Error transferring asset: {str(e)}")
            return False
    
    def dispose_asset(self, asset_id: str, disposal_type: str, disposal_date: date, 
                     disposal_amount: Decimal, reason: str) -> bool:
        """Dispose asset (sell or scrap)"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return False
            
            if asset.status in [AssetStatus.SOLD, AssetStatus.SCRAPPED]:
                self.logger.warning(f"Asset {asset_id} is already disposed")
                return False
            
            # Update asset status
            asset.status = AssetStatus.SOLD if disposal_type == "sale" else AssetStatus.SCRAPPED
            asset.is_active = False
            asset.updated_at = datetime.now()
            
            # Create disposal journal entry
            journal_entry = {
                "date": disposal_date,
                "reference": f"DIS_{asset_id}",
                "description": f"Asset disposal: {reason}",
                "transactions": [
                    {
                        "account_id": "999999",  # Cash/Bank account
                        "debit_amount": disposal_amount,
                        "credit_amount": Decimal('0'),
                        "description": f"Proceeds from asset disposal"
                    },
                    {
                        "account_id": "999999",  # Accumulated Depreciation account
                        "debit_amount": Decimal('0'),
                        "credit_amount": next((d.accumulated_amount for d in reversed(self.depreciation[asset_id])), Decimal('0')),
                        "description": "Accumulated depreciation"
                    },
                    {
                        "account_id": "999999",  # Asset account
                        "debit_amount": Decimal('0'),
                        "credit_amount": asset.purchase_price,
                        "description": "Asset cost"
                    }
                ]
            }
            
            if not self.accounting_system.add_journal_entry(journal_entry):
                return False
            
            self.logger.info(f"Asset {asset_id} disposed")
            return True
        except Exception as e:
            self.logger.error(f"Error disposing asset: {str(e)}")
            return False
    
    def get_asset_details(self, asset_id: str) -> Dict[str, Any]:
        """Get asset details including components, maintenance, depreciation and transfers"""
        try:
            asset = self.assets.get(asset_id)
            if not asset:
                return {}
            
            return {
                "asset": {
                    "id": asset.id,
                    "code": asset.code,
                    "name": asset.name,
                    "type": asset.type.value,
                    "description": asset.description,
                    "purchase_date": asset.purchase_date.isoformat(),
                    "purchase_price": asset.purchase_price,
                    "salvage_value": asset.salvage_value,
                    "useful_life": asset.useful_life,
                    "depreciation_method": asset.depreciation_method.value,
                    "location": asset.location,
                    "department": asset.department_id,
                    "status": asset.status.value,
                    "is_active": asset.is_active
                },
                "components": [
                    {
                        "id": component.id,
                        "name": component.name,
                        "description": component.description,
                        "purchase_date": component.purchase_date.isoformat(),
                        "purchase_price": component.purchase_price,
                        "salvage_value": component.salvage_value,
                        "useful_life": component.useful_life,
                        "depreciation_method": component.depreciation_method.value
                    }
                    for component in self.components.get(asset_id, [])
                ],
                "maintenance": [
                    {
                        "id": maintenance.id,
                        "type": maintenance.type,
                        "description": maintenance.description,
                        "start_date": maintenance.start_date.isoformat(),
                        "end_date": maintenance.end_date.isoformat() if maintenance.end_date else None,
                        "cost": maintenance.cost,
                        "performed_by": maintenance.performed_by,
                        "status": maintenance.status
                    }
                    for maintenance in self.maintenance.get(asset_id, [])
                ],
                "depreciation": [
                    {
                        "id": dep.id,
                        "period_start": dep.period_start.isoformat(),
                        "period_end": dep.period_end.isoformat(),
                        "amount": dep.amount,
                        "accumulated_amount": dep.accumulated_amount,
                        "book_value": dep.book_value
                    }
                    for dep in self.depreciation.get(asset_id, [])
                ],
                "transfers": [
                    {
                        "id": transfer.id,
                        "from_location": transfer.from_location,
                        "to_location": transfer.to_location,
                        "from_department": transfer.from_department,
                        "to_department": transfer.to_department,
                        "transfer_date": transfer.transfer_date.isoformat(),
                        "reason": transfer.reason,
                        "approved_by": transfer.approved_by
                    }
                    for transfer in self.transfers.get(asset_id, [])
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting asset details: {str(e)}")
            return {}
    
    def get_asset_list(self, asset_type: Optional[AssetType] = None, 
                      status: Optional[AssetStatus] = None,
                      department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of assets with optional filters"""
        try:
            assets = []
            for asset in self.assets.values():
                if (asset_type and asset.type != asset_type) or \
                   (status and asset.status != status) or \
                   (department_id and asset.department_id != department_id):
                    continue
                
                # Get latest depreciation
                latest_depreciation = next(
                    (d for d in reversed(self.depreciation.get(asset.id, []))),
                    None
                )
                
                assets.append({
                    "id": asset.id,
                    "code": asset.code,
                    "name": asset.name,
                    "type": asset.type.value,
                    "purchase_date": asset.purchase_date.isoformat(),
                    "purchase_price": asset.purchase_price,
                    "location": asset.location,
                    "department": asset.department_id,
                    "status": asset.status.value,
                    "book_value": latest_depreciation.book_value if latest_depreciation else asset.purchase_price,
                    "is_active": asset.is_active
                })
            
            return sorted(assets, key=lambda x: x["name"])
        except Exception as e:
            self.logger.error(f"Error getting asset list: {str(e)}")
            return []
    
    def add_insurance(self, insurance: Insurance) -> bool:
        """Add insurance policy for asset"""
        try:
            if insurance.asset_id not in self.assets:
                self.logger.error(f"Asset {insurance.asset_id} not found")
                return False
            
            if insurance.id in [i.id for i in self.insurance.get(insurance.asset_id, [])]:
                self.logger.warning(f"Insurance with ID {insurance.id} already exists")
                return False
            
            if insurance.asset_id not in self.insurance:
                self.insurance[insurance.asset_id] = []
            
            self.insurance[insurance.asset_id].append(insurance)
            self.claims[insurance.id] = []
            
            # Create insurance journal entry
            journal_entry = {
                "date": insurance.start_date,
                "reference": f"INS_{insurance.id}",
                "description": f"Insurance premium for {insurance.type.value}",
                "transactions": [
                    {
                        "account_id": "999999",  # Insurance expense account
                        "debit_amount": insurance.premium_amount,
                        "credit_amount": Decimal('0'),
                        "description": f"Insurance premium for {insurance.type.value}"
                    },
                    {
                        "account_id": "999999",  # Prepaid insurance account
                        "debit_amount": Decimal('0'),
                        "credit_amount": insurance.premium_amount,
                        "description": "Prepaid insurance"
                    }
                ]
            }
            
            if not self.accounting_system.add_journal_entry(journal_entry):
                return False
            
            self.logger.info(f"Insurance added for asset {insurance.asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding insurance: {str(e)}")
            return False
    
    def add_insurance_claim(self, claim: InsuranceClaim) -> bool:
        """Add insurance claim"""
        try:
            insurance = next((i for i in self.insurance.get(claim.insurance_id, []) 
                            if i.id == claim.insurance_id), None)
            if not insurance:
                self.logger.error(f"Insurance {claim.insurance_id} not found")
                return False
            
            if claim.id in [c.id for c in self.claims.get(claim.insurance_id, [])]:
                self.logger.warning(f"Claim with ID {claim.id} already exists")
                return False
            
            self.claims[claim.insurance_id].append(claim)
            self.logger.info(f"Insurance claim added for insurance {claim.insurance_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding insurance claim: {str(e)}")
            return False
    
    def update_claim_status(self, claim_id: str, insurance_id: str, 
                          status: str, payment_date: Optional[date] = None,
                          payment_amount: Decimal = Decimal('0')) -> bool:
        """Update insurance claim status"""
        try:
            claim = next((c for c in self.claims.get(insurance_id, []) 
                         if c.id == claim_id), None)
            if not claim:
                return False
            
            claim.status = status
            if payment_date:
                claim.payment_date = payment_date
                claim.payment_amount = payment_amount
                
                # Create claim payment journal entry
                journal_entry = {
                    "date": payment_date,
                    "reference": f"CLM_{claim_id}",
                    "description": f"Insurance claim payment for {claim.description}",
                    "transactions": [
                        {
                            "account_id": "999999",  # Cash/Bank account
                            "debit_amount": payment_amount,
                            "credit_amount": Decimal('0'),
                            "description": "Insurance claim payment"
                        },
                        {
                            "account_id": "999999",  # Insurance receivable account
                            "debit_amount": Decimal('0'),
                            "credit_amount": payment_amount,
                            "description": "Insurance claim receivable"
                        }
                    ]
                }
                
                if not self.accounting_system.add_journal_entry(journal_entry):
                    return False
            
            claim.updated_at = datetime.now()
            self.logger.info(f"Insurance claim {claim_id} status updated")
            return True
        except Exception as e:
            self.logger.error(f"Error updating claim status: {str(e)}")
            return False
    
    def add_document(self, document: AssetDocument) -> bool:
        """Add document for asset"""
        try:
            if document.asset_id not in self.assets:
                self.logger.error(f"Asset {document.asset_id} not found")
                return False
            
            if document.id in [d.id for d in self.documents.get(document.asset_id, [])]:
                self.logger.warning(f"Document with ID {document.id} already exists")
                return False
            
            # Create asset-specific directory
            asset_dir = os.path.join(self.document_base_path, document.asset_id)
            if not os.path.exists(asset_dir):
                os.makedirs(asset_dir)
            
            # Move file to asset directory
            new_file_path = os.path.join(asset_dir, document.file_name)
            if os.path.exists(document.file_path):
                os.rename(document.file_path, new_file_path)
                document.file_path = new_file_path
            
            if document.asset_id not in self.documents:
                self.documents[document.asset_id] = []
            
            self.documents[document.asset_id].append(document)
            self.logger.info(f"Document added for asset {document.asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding document: {str(e)}")
            return False
    
    def delete_document(self, document_id: str, asset_id: str) -> bool:
        """Delete document"""
        try:
            document = next((d for d in self.documents.get(asset_id, []) 
                           if d.id == document_id), None)
            if not document:
                return False
            
            # Delete file
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Remove from list
            self.documents[asset_id].remove(document)
            self.logger.info(f"Document {document_id} deleted")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_insurance_details(self, insurance_id: str, asset_id: str) -> Dict[str, Any]:
        """Get insurance details including claims"""
        try:
            insurance = next((i for i in self.insurance.get(asset_id, []) 
                            if i.id == insurance_id), None)
            if not insurance:
                return {}
            
            return {
                "insurance": {
                    "id": insurance.id,
                    "type": insurance.type.value,
                    "insurance_company": insurance.insurance_company,
                    "policy_number": insurance.policy_number,
                    "start_date": insurance.start_date.isoformat(),
                    "end_date": insurance.end_date.isoformat(),
                    "coverage_amount": insurance.coverage_amount,
                    "premium_amount": insurance.premium_amount,
                    "deductible": insurance.deductible,
                    "description": insurance.description,
                    "is_active": insurance.is_active
                },
                "claims": [
                    {
                        "id": claim.id,
                        "claim_number": claim.claim_number,
                        "incident_date": claim.incident_date.isoformat(),
                        "description": claim.description,
                        "claim_amount": claim.claim_amount,
                        "status": claim.status,
                        "payment_date": claim.payment_date.isoformat() if claim.payment_date else None,
                        "payment_amount": claim.payment_amount
                    }
                    for claim in self.claims.get(insurance_id, [])
                ]
            }
        except Exception as e:
            self.logger.error(f"Error getting insurance details: {str(e)}")
            return {}
    
    def get_document_list(self, asset_id: str, 
                         document_type: Optional[DocumentType] = None) -> List[Dict[str, Any]]:
        """Get list of documents for asset"""
        try:
            documents = []
            for document in self.documents.get(asset_id, []):
                if document_type and document.type != document_type:
                    continue
                
                documents.append({
                    "id": document.id,
                    "type": document.type.value,
                    "title": document.title,
                    "description": document.description,
                    "file_name": document.file_name,
                    "file_size": document.file_size,
                    "file_type": document.file_type,
                    "upload_date": document.upload_date.isoformat(),
                    "uploaded_by": document.uploaded_by,
                    "is_active": document.is_active
                })
            
            return sorted(documents, key=lambda x: x["upload_date"], reverse=True)
        except Exception as e:
            self.logger.error(f"Error getting document list: {str(e)}")
            return [] 