"""
Projects Module — Tests
TOP WorX ERP System
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from app.models.projects import (
    Project, ProjectMilestone, ProjectResource, ProjectRisk,
    ProjectStatus, ProjectPriority, MilestoneStatus, RiskStatus, ResourceType,
)
from app.services.projects_service import ProjectsService, ProjectsError


class TestProjectsService:
    """Tests for Projects service layer."""
    
    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        assert ProjectStatus.PLANNING.value == "planning"
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.ON_HOLD.value == "on_hold"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.CANCELLED.value == "cancelled"
    
    def test_project_priority_enum(self):
        """Test ProjectPriority enum values."""
        assert ProjectPriority.LOW.value == "low"
        assert ProjectPriority.MEDIUM.value == "medium"
        assert ProjectPriority.HIGH.value == "high"
        assert ProjectPriority.CRITICAL.value == "critical"
    
    def test_milestone_status_enum(self):
        """Test MilestoneStatus enum values."""
        assert MilestoneStatus.PENDING.value == "pending"
        assert MilestoneStatus.IN_PROGRESS.value == "in_progress"
        assert MilestoneStatus.COMPLETED.value == "completed"
        assert MilestoneStatus.DELAYED.value == "delayed"
    
    def test_risk_status_enum(self):
        """Test RiskStatus enum values."""
        assert RiskStatus.OPEN.value == "open"
        assert RiskStatus.MITIGATED.value == "mitigated"
        assert RiskStatus.CLOSED.value == "closed"
    
    def test_resource_type_enum(self):
        """Test ResourceType enum values."""
        assert ResourceType.HUMAN.value == "human"
        assert ResourceType.MATERIAL.value == "material"
        assert ResourceType.EQUIPMENT.value == "equipment"
        assert ResourceType.FINANCIAL.value == "financial"
    
    def test_projects_error_exception(self):
        """Test ProjectsError exception."""
        error = ProjectsError("Test error")
        assert str(error) == "Test error"
    
    def test_project_model_fields(self):
        """Test Project model has required fields."""
        # This is a structural test - verifying model definition
        from app.models.projects import Project
        import inspect
        
        # Get model columns
        columns = [c.name for c in Project.__table__.columns]
        
        required_columns = [
            'id', 'code', 'name', 'status', 'priority',
            'start_date', 'end_date', 'budget', 'actual_cost', 'progress',
            'created_by_id', 'created_at', 'updated_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_milestone_model_fields(self):
        """Test ProjectMilestone model has required fields."""
        from app.models.projects import ProjectMilestone
        columns = [c.name for c in ProjectMilestone.__table__.columns]
        
        required_columns = [
            'id', 'project_id', 'name', 'due_date', 'status',
            'created_by_id', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_risk_model_fields(self):
        """Test ProjectRisk model has required fields."""
        from app.models.projects import ProjectRisk
        columns = [c.name for c in ProjectRisk.__table__.columns]
        
        required_columns = [
            'id', 'project_id', 'name', 'probability', 'impact',
            'status', 'created_by_id', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
    
    def test_resource_model_fields(self):
        """Test ProjectResource model has required fields."""
        from app.models.projects import ProjectResource
        columns = [c.name for c in ProjectResource.__table__.columns]
        
        required_columns = [
            'id', 'project_id', 'name', 'type', 'quantity',
            'unit_cost', 'total_cost', 'created_by_id', 'created_at'
        ]
        
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"


class TestProjectsSchemas:
    """Tests for Projects schemas."""
    
    def test_project_create_schema(self):
        """Test ProjectCreate schema."""
        from app.schemas.projects import ProjectCreate
        
        data = ProjectCreate(
            code="PRJ-001",
            name="Test Project",
            start_date=date.today(),
            end_date=date.today(),
        )
        
        assert data.code == "PRJ-001"
        assert data.name == "Test Project"
        assert data.status == ProjectStatus.PLANNING
        assert data.priority == ProjectPriority.MEDIUM
        assert data.budget == Decimal("0")
    
    def test_project_response_schema(self):
        """Test ProjectResponse schema."""
        from app.schemas.projects import ProjectResponse
        
        data = ProjectResponse(
            id=1,
            code="PRJ-001",
            name="Test Project",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            start_date=date.today(),
            end_date=date.today(),
            budget=Decimal("1000000"),
            actual_cost=Decimal("500000"),
            progress=Decimal("50"),
            created_by_id=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.id == 1
        assert data.status == ProjectStatus.ACTIVE
        assert data.progress == Decimal("50")


class TestProjectsEndpoints:
    """Tests for Projects API endpoints."""
    
    def test_projects_router_exists(self):
        """Test that projects router is properly defined."""
        from app.api.v1.endpoints.projects import router
        assert router is not None
        assert hasattr(router, 'routes')
    
    def test_projects_endpoints_defined(self):
        """Test that all required endpoints are defined."""
        from app.api.v1.endpoints.projects import router
        
        routes = [route.path for route in router.routes]
        
        # Check main CRUD endpoints
        assert "" in routes  # List/Create
        assert "/{project_id}" in routes  # Get/Update/Delete
        assert "/{project_id}/milestones" in routes  # Milestones
        assert "/{project_id}/resources" in routes  # Resources
        assert "/{project_id}/risks" in routes  # Risks
        assert "/dashboard/stats" in routes  # Dashboard


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
