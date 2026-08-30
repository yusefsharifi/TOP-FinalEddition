/**
 * AI Integration E2E Test
 * TOP WorX ERP System
 * 
 * Tests AI integration across all modules:
 * - AI Dashboard rendering
 * - AI Chat functionality
 * - Module-specific AI features
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';

// Mock API client
jest.mock('../../../api/ai', () => ({
  getAIDashboard: jest.fn().mockResolvedValue({
    usage: {
      total_requests: 100,
      total_tokens: 50000,
      total_cost: 1.5,
      avg_duration_ms: 250,
    },
    unread_insights: 5,
    active_workflows: 3,
    recent_conversations: [
      {
        id: 1,
        title: 'Test Conversation',
        module: 'inventory',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ],
    openai_configured: true,
    anthropic_configured: false,
    default_model: 'gpt-4o',
  }),
  getAllAIInsights: jest.fn().mockResolvedValue({
    modules_requested: ['inventory', 'finance', 'hr', 'sales'],
    modules_with_data: ['inventory', 'finance'],
    insights: {
      inventory: {
        stockout_prediction: { total_items_at_risk: 2 },
        smart_reorder: { total_suggestions: 5 },
      },
      finance: {
        cashflow_prediction: { total_projected_30_days: 1000000 },
        expense_anomaly: { total_anomalies: 1 },
      },
    },
  }),
  getInventoryStockoutPrediction: jest.fn().mockResolvedValue({
    total_items_at_risk: 2,
    critical_items: [],
    warning_items: [],
  }),
  getFinanceCashflowPrediction: jest.fn().mockResolvedValue({
    predictions: [],
    total_projected_30_days: 1000000,
  }),
  getHRAttritionPrediction: jest.fn().mockResolvedValue({
    total_at_risk: 3,
    high_risk: [],
    medium_risk: [],
  }),
  getSalesRevenueForecast: jest.fn().mockResolvedValue({
    historical_avg_monthly: 500000,
    trend: 0.05,
    forecast: [],
    confidence: 75,
  }),
}));

// Mock React Query
jest.mock('@tanstack/react-query', () => ({
  QueryClient: jest.fn().mockImplementation(() => ({
    defaultOptions: {
      queries: { retry: false },
    },
  })),
  QueryClientProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useQuery: jest.fn().mockReturnValue({
    data: null,
    isLoading: false,
    error: null,
  }),
}));

describe('AI Integration', () => {
  describe('AI Dashboard', () => {
    it('renders AI Dashboard with statistics', async () => {
      const AIDashboard = require('../../../app/components/ai/AIDashboard').default;
      
      render(
        <BrowserRouter>
          <ConfigProvider>
            <AIDashboard />
          </ConfigProvider>
        </BrowserRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('AI Dashboard')).toBeInTheDocument();
      });
      
      // Check if statistics are displayed
      expect(screen.getByText('Total AI Requests')).toBeInTheDocument();
      expect(screen.getByText('Tokens Used')).toBeInTheDocument();
      expect(screen.getByText('Total Cost')).toBeInTheDocument();
      expect(screen.getByText('Unread Insights')).toBeInTheDocument();
    });

    it('displays AI configuration status', async () => {
      const AIDashboard = require('../../../app/components/ai/AIDashboard').default;
      
      render(
        <BrowserRouter>
          <ConfigProvider>
            <AIDashboard />
          </ConfigProvider>
        </BrowserRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('AI Configuration')).toBeInTheDocument();
      });
      
      expect(screen.getByText('OpenAI:')).toBeInTheDocument();
      expect(screen.getByText('Configured')).toBeInTheDocument();
    });

    it('displays module AI status', async () => {
      const AIDashboard = require('../../../app/components/ai/AIDashboard').default;
      
      render(
        <BrowserRouter>
          <ConfigProvider>
            <AIDashboard />
          </ConfigProvider>
        </BrowserRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Module AI Status')).toBeInTheDocument();
      });
      
      expect(screen.getByText('Inventory')).toBeInTheDocument();
      expect(screen.getByText('Finance')).toBeInTheDocument();
      expect(screen.getByText('HR')).toBeInTheDocument();
    });
  });

  describe('AI API Client', () => {
    it('exports all AI API functions', () => {
      const aiApi = require('../../../api/ai');
      
      // Chat functions
      expect(aiApi.aiChat).toBeDefined();
      expect(aiApi.getAIConversations).toBeDefined();
      expect(aiApi.createAIConversation).toBeDefined();
      expect(aiApi.getAIInsights).toBeDefined();
      expect(aiApi.getAIUsage).toBeDefined();
      
      // Module-specific functions
      expect(aiApi.getInventoryStockoutPrediction).toBeDefined();
      expect(aiApi.getInventorySmartReorder).toBeDefined();
      expect(aiApi.getInventoryAnomalyDetection).toBeDefined();
      expect(aiApi.getFinanceCashflowPrediction).toBeDefined();
      expect(aiApi.getFinanceExpenseAnomaly).toBeDefined();
      expect(aiApi.getHRAttritionPrediction).toBeDefined();
      expect(aiApi.getSalesRevenueForecast).toBeDefined();
      expect(aiApi.getSalesChurnPrediction).toBeDefined();
      expect(aiApi.getCRMLeadScore).toBeDefined();
      expect(aiApi.getProcurementSupplierRisk).toBeDefined();
      expect(aiApi.getQualityDefectPrediction).toBeDefined();
      expect(aiApi.getHSEIncidentPrediction).toBeDefined();
      expect(aiApi.getHSESafetyScore).toBeDefined();
      expect(aiApi.getProjectsRiskAssessment).toBeDefined();
      expect(aiApi.getSupportTicketSentiment).toBeDefined();
      
      // Dashboard functions
      expect(aiApi.getAllAIInsights).toBeDefined();
      expect(aiApi.getAIDashboard).toBeDefined();
    });
  });

  describe('AI Module Integration Endpoints', () => {
    it('has correct endpoint paths', () => {
      const aiApi = require('../../../api/ai');
      
      // Test that functions make correct API calls
      const mockApi = { get: jest.fn(), post: jest.fn() };
      jest.mock('../../../core/api/client', () => ({
        default: mockApi,
      }));
      
      // Inventory endpoints
      aiApi.getInventoryStockoutPrediction();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/inventory/stockout-prediction');
      
      aiApi.getInventorySmartReorder();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/inventory/smart-reorder');
      
      // Finance endpoints
      aiApi.getFinanceCashflowPrediction();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/finance/cashflow-prediction');
      
      // HR endpoints
      aiApi.getHRAttritionPrediction();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/hr/attrition-prediction');
      
      // Sales endpoints
      aiApi.getSalesRevenueForecast();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/sales/revenue-forecast');
      
      // CRM endpoints
      aiApi.getCRMLeadScore(123);
      expect(mockApi.get).toHaveBeenCalledWith('/ai/crm/lead-scoring/123');
      
      // Procurement endpoints
      aiApi.getProcurementSupplierRisk();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/procurement/supplier-risk');
      
      // Quality endpoints
      aiApi.getQualityDefectPrediction();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/quality/defect-prediction');
      
      // HSE endpoints
      aiApi.getHSEIncidentPrediction();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/hse/incident-prediction');
      
      aiApi.getHSESafetyScore();
      expect(mockApi.get).toHaveBeenCalledWith('/ai/hse/safety-score');
      
      // Projects endpoints
      aiApi.getProjectsRiskAssessment(456);
      expect(mockApi.get).toHaveBeenCalledWith('/ai/projects/456/risk-assessment');
      
      // Support endpoints
      aiApi.getSupportTicketSentiment(789);
      expect(mockApi.get).toHaveBeenCalledWith('/ai/support/ticket-sentiment/789');
    });
  });
});
