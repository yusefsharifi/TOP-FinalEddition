import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import {
  AISummaryWidget,
  AIInsightsWidget,
  AIRecommendationsWidget,
  AIPredictionsWidget,
  AICorrelationsWidget,
  AIQuickActionsWidget,
  AIActivityWidget,
} from '../app/components/dashboard/AIDashboardWidgets';

// Mock fetch
beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({
      modules_analyzed: 10,
      total_insights: 25,
      critical_alerts: 3,
      insights: [],
      recommendations: [],
      predictions: [],
    }),
  }) as jest.Mock;
});

afterEach(() => {
  jest.restoreAllMocks();
});

const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('AIDashboardWidgets', () => {
  describe('AISummaryWidget', () => {
    it('renders without crashing', async () => {
      render(<AISummaryWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/تحلیل هوشمند/)).toBeInTheDocument();
      });
    });
  });

  describe('AIInsightsWidget', () => {
    it('renders without crashing', async () => {
      render(<AIInsightsWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/بینش‌های هوشمند/)).toBeInTheDocument();
      });
    });
  });

  describe('AIRecommendationsWidget', () => {
    it('renders without crashing', async () => {
      render(<AIRecommendationsWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/پیشنهادات/)).toBeInTheDocument();
      });
    });
  });

  describe('AIPredictionsWidget', () => {
    it('renders without crashing', async () => {
      render(<AIPredictionsWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/پیش‌بینی‌ها/)).toBeInTheDocument();
      });
    });
  });

  describe('AICorrelationsWidget', () => {
    it('renders without crashing', async () => {
      render(<AICorrelationsWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/ارتباطات/)).toBeInTheDocument();
      });
    });
  });

  describe('AIQuickActionsWidget', () => {
    it('renders quick action buttons', () => {
      render(<AIQuickActionsWidget />, { wrapper: Wrapper });
      expect(screen.getByText(/دستیار هوشمند/)).toBeInTheDocument();
    });
  });

  describe('AIActivityWidget', () => {
    it('renders without crashing', async () => {
      render(<AIActivityWidget />, { wrapper: Wrapper });
      await waitFor(() => {
        expect(screen.getByText(/فعالیت اخیر/)).toBeInTheDocument();
      });
    });
  });
});
