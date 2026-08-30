"""
Budget Module — Tests
TOP WorX ERP System
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.budget import (
    Budget, BudgetLine, BudgetRevision, BudgetPerformance,
    BudgetType, BudgetStatus, BudgetPeriod,
)
from app.services.budget_service import BudgetService, BudgetError


class TestBudgetService:
    """Tests for Budget service layer."""
    
    def test_budget_type_enum(self):
        """Test BudgetType enum values."""
        assert BudgetType.OPERATIONAL.value == "operational"
        assert BudgetType.CAPITAL.value == "capital"
        assert BudgetType.CASH.value == "cash"
        assert BudgetType.PROJECT.value == "project"
    
    def test_budget_status_enum(self):
        """Test BudgetStatus enum values."""
        assert BudgetStatus.DRAFT.value == "draft"
        assert BudgetStatus.PENDING.value == "pending"
        assert BudgetStatus.APPROVED.value == "approved"
        assert BudgetStatus.REJECTED.value == "rejected"
        assert BudgetStatus.ACTIVE.value == "active"
        assert BudgetStatus.CLOSED.value == "closed"
    
    def test_budget_period_enum(self):
        """Test BudgetPeriod enum values."""
        assert BudgetPeriod.MONTHLY.value == "monthly"
        assert BudgetPeriod.QUARTERLY.value == "quarterly"
        assert BudgetPeriod.SEMI_ANNUAL.value == "semi_annual"
        assert BudgetPeriod.ANNUAL.value == "annual"
    
    def test_budget_error_exception(self):
        """Test BudgetError exception."""
        error = BudgetError("Test error")
        assert str(error) == "Test error"
    
    def test_budget_model_fields(self):
        """Test Budget model has required fields."""
        from app.models.budget import Budget
        columns = [c.name for c in Budget.__table__.columns]
        
        required_columns = [
            'id', 'code', 'name', 'type', 'period', 'fiscal_year',
            'start_date', 'end_date', 'status',
            'created_by_id', 'created_at', 'updated_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_budget_line_model_fields(self):
        """Test BudgetLine model has required fields."""
        from app.models.budget import BudgetLine
        columns = [c.name for c in BudgetLine.__table__.columns]
        
        required_columns = [
            'id', 'budget_id', 'account_id', 'amount',
            'created_by_id', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_budget_revision_model_fields(self):
        """Test BudgetRevision model has required fields."""
        from app.models.budget import BudgetRevision
        columns = [c.name for c in BudgetRevision.__table__.columns]
        
        required_columns = [
            'id', 'budget_id', 'revision_number', 'description',
            'status', 'created_by_id', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_budget_performance_model_fields(self):
        """Test BudgetPerformance model has required fields."""
        from app.models.budget import BudgetPerformance
        columns = [c.name for c in BudgetPerformance.__table__.columns]
        
        required_columns = [
            'id', 'budget_id', 'account_id', 'period',
            'budget_amount', 'actual_amount', 'variance_amount',
            'variance_percentage', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"


class TestBudgetSchemas:
    """Tests for Budget schemas."""
    
    def test_budget_create_schema(self):
        """Test BudgetCreate schema."""
        from app.schemas.budget import BudgetCreate
        
        data = BudgetCreate(
            code="BUD-2024-001",
            name="Annual Operating Budget",
            type=BudgetType.OPERATIONAL,
            period=BudgetPeriod.ANNUAL,
            fiscal_year="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
        
        assert data.code == "BUD-2024-001"
        assert data.name == "Annual Operating Budget"
        assert data.type == BudgetType.OPERATIONAL
        assert data.period == BudgetPeriod.ANNUAL
        assert data.fiscal_year == "2024"
    
    def test_budget_response_schema(self):
        """Test BudgetResponse schema."""
        from app.schemas.budget import BudgetResponse
        
        data = BudgetResponse(
            id=1,
            code="BUD-2024-001",
            name="Annual Operating Budget",
            type=BudgetType.OPERATIONAL,
            period=BudgetPeriod.ANNUAL,
            fiscal_year="2024",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            status=BudgetStatus.ACTIVE,
            created_by_id=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.id == 1
        assert data.status == BudgetStatus.ACTIVE
        assert data.type == BudgetType.OPERATIONAL
    
    def test_budget_line_create_schema(self):
        """Test BudgetLineCreate schema."""
        from app.schemas.budget import BudgetLineCreate
        
        data = BudgetLineCreate(
            account_id=1,
            amount=Decimal("1000000"),
            description="Salary expenses",
        )
        
        assert data.account_id == 1
        assert data.amount == Decimal("1000000")
        assert data.description == "Salary expenses"


class TestBudgetEndpoints:
    """Tests for Budget API endpoints."""
    
    def test_budget_router_exists(self):
        """Test that budget router is properly defined."""
        from app.api.v1.endpoints.budget import router
        assert router is not None
        assert hasattr(router, 'routes')
    
    def test_budget_endpoints_defined(self):
        """Test that all required endpoints are defined."""
        from app.api.v1.endpoints.budget import router
        
        routes = [route.path for route in router.routes]
        
        # Check main CRUD endpoints
        assert "" in routes  # List/Create
        assert "/{budget_id}" in routes  # Get/Update/Delete
        assert "/{budget_id}/submit" in routes  # Submit
        assert "/{budget_id}/approve" in routes  # Approve
        assert "/{budget_id}/activate" in routes  # Activate
        assert "/{budget_id}/close" in routes  # Close
        assert "/{budget_id}/lines" in routes  # Lines
        assert "/{budget_id}/revisions" in routes  # Revisions
        assert "/dashboard/stats" in routes  # Dashboard


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
