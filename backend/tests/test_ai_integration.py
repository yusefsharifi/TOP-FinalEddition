"""
AI Module Integration — Tests
TOP WorX ERP System
"""
import pytest
from datetime import date, datetime
from decimal import Decimal

from app.core.ai.module_integration import AIModuleIntegration, get_ai_module_integration


class TestAIModuleIntegration:
    """Tests for AI module integration service."""
    
    def test_module_integration_class_exists(self):
        """Test that AIModuleIntegration class exists."""
        assert AIModuleIntegration is not None
    
    def test_factory_function_exists(self):
        """Test that get_ai_module_integration factory exists."""
        assert get_ai_module_integration is not None
        assert callable(get_ai_module_integration)
    
    def test_integration_methods_exist(self):
        """Test that all required AI integration methods exist."""
        methods = [
            # Inventory AI
            'inventory_stockout_prediction',
            'inventory_smart_reorder_suggestions',
            'inventory_anomaly_detection',
            # Finance AI
            'finance_cashflow_prediction',
            'finance_expense_anomaly_detection',
            # HR AI
            'hr_attrition_prediction',
            # Sales AI
            'sales_revenue_forecast',
            'sales_churn_prediction',
            # CRM AI
            'crm_lead_scoring',
            # Procurement AI
            'procurement_supplier_risk_analysis',
            # Quality AI
            'quality_defect_prediction',
            # HSE AI
            'hse_incident_prediction',
            'hse_safety_score',
            # Projects AI
            'projects_risk_assessment',
            # Support AI
            'support_ticket_sentiment',
        ]
        
        for method in methods:
            assert hasattr(AIModuleIntegration, method), f"Missing method: {method}"
            assert callable(getattr(AIModuleIntegration, method)), f"Not callable: {method}"


class TestAIEndpoints:
    """Tests for AI module integration endpoints."""
    
    def test_ai_module_integration_router_exists(self):
        """Test that AI module integration router is properly defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        assert router is not None
        assert hasattr(router, 'routes')
    
    def test_inventory_ai_endpoints_defined(self):
        """Test that Inventory AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/inventory/stockout-prediction" in routes
        assert "/inventory/smart-reorder" in routes
        assert "/inventory/anomaly-detection" in routes
    
    def test_finance_ai_endpoints_defined(self):
        """Test that Finance AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/finance/cashflow-prediction" in routes
        assert "/finance/expense-anomaly" in routes
    
    def test_hr_ai_endpoints_defined(self):
        """Test that HR AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/hr/attrition-prediction" in routes
    
    def test_sales_ai_endpoints_defined(self):
        """Test that Sales AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/sales/revenue-forecast" in routes
        assert "/sales/churn-prediction" in routes
    
    def test_crm_ai_endpoints_defined(self):
        """Test that CRM AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/crm/lead-scoring/{lead_id}" in routes
    
    def test_procurement_ai_endpoints_defined(self):
        """Test that Procurement AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/procurement/supplier-risk" in routes
    
    def test_quality_ai_endpoints_defined(self):
        """Test that Quality AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/quality/defect-prediction" in routes
    
    def test_hse_ai_endpoints_defined(self):
        """Test that HSE AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/hse/incident-prediction" in routes
        assert "/hse/safety-score" in routes
    
    def test_projects_ai_endpoints_defined(self):
        """Test that Projects AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/projects/{project_id}/risk-assessment" in routes
    
    def test_support_ai_endpoints_defined(self):
        """Test that Support AI endpoints are defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/support/ticket-sentiment/{ticket_id}" in routes
    
    def test_all_insights_endpoint_defined(self):
        """Test that all-insights endpoint is defined."""
        from app.api.v1.endpoints.ai_module_integration import router
        
        routes = [route.path for route in router.routes]
        
        assert "/dashboard/all-insights" in routes


class TestAICoreEngine:
    """Tests for AI core engine."""
    
    def test_ai_engine_class_exists(self):
        """Test that AIEngine class exists."""
        from app.core.ai.engine import AIEngine
        assert AIEngine is not None
    
    def test_ai_engine_factory_exists(self):
        """Test that get_ai_engine factory exists."""
        from app.core.ai.engine import get_ai_engine
        assert get_ai_engine is not None
        assert callable(get_ai_engine)


class TestAICoreModules:
    """Tests for AI core modules."""
    
    def test_ai_analytics_module_exists(self):
        """Test that AI analytics module exists."""
        from app.core.ai import analytics
        assert analytics is not None
    
    def test_ai_reports_module_exists(self):
        """Test that AI reports module exists."""
        from app.core.ai import reports
        assert reports is not None
    
    def test_ai_assistant_module_exists(self):
        """Test that AI assistant module exists."""
        from app.core.ai import assistant
        assert assistant is not None
    
    def test_ai_automation_module_exists(self):
        """Test that AI automation module exists."""
        from app.core.ai import automation
        assert automation is not None
    
    def test_workflow_handlers_module_exists(self):
        """Test that workflow handlers module exists."""
        from app.core.ai import workflow_handlers
        assert workflow_handlers is not None
    
    def test_workflow_scheduler_module_exists(self):
        """Test that workflow scheduler module exists."""
        from app.core.ai import workflow_scheduler
        assert workflow_scheduler is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
