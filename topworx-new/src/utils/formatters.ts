// src/utils/formatters.ts
// ============================================================================
// Formatting Utilities
// ============================================================================

// ─────────────────────────────────────────────────────────────────────────────
// Number Formatters
// ─────────────────────────────────────────────────────────────────────────────

export function formatIRR(value: number | string, digits = 0): string {
  const n = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(n)) return '-';
  
  if (Math.abs(n) >= 1_000_000_000) {
    return `${(n / 1_000_000_000).toFixed(digits)} میلیارد`;
  }
  if (Math.abs(n) >= 1_000_000) {
    return `${(n / 1_000_000).toFixed(digits)} میلیون`;
  }
  return new Intl.NumberFormat('fa-IR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(n);
}

export function formatDecimal(value: string | number, digits = 2): string {
  const n = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(n)) return '-';
  return new Intl.NumberFormat('fa-IR', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(n);
}

export function formatPct(value: number | string, digits = 1): string {
  const n = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(n)) return '-';
  return `${n.toFixed(digits)}٪`;
}

// ─────────────────────────────────────────────────────────────────────────────
// Date Formatters (Jalali)
// ─────────────────────────────────────────────────────────────────────────────

export const JALALI_MONTHS = [
  'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
  'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
];

export function formatJalaliDate(dateString: string): string {
  const date = new Date(dateString);
  // Note: In production, use a proper Jalali conversion library like 'moment-jalaali'
  // or '@date-io/jalaali' with MUI date pickers
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
}

export function formatJalaliMonth(month: number): string {
  return JALALI_MONTHS[month - 1] || '';
}

// ─────────────────────────────────────────────────────────────────────────────
// Status Helpers
// ─────────────────────────────────────────────────────────────────────────────

import { InvoiceStatus, QuoteStatus, PaymentStatus, LeaveStatus, PayrollPeriodStatus } from '../types';

export const invoiceStatusColors: Record<InvoiceStatus, 'default' | 'warning' | 'error' | 'success' | 'info'> = {
  draft: 'default',
  issued: 'info',
  partial_paid: 'warning',
  paid: 'success',
  overdue: 'error',
  cancelled: 'default',
};

export const invoiceStatusLabels: Record<InvoiceStatus, string> = {
  draft: 'پیش‌نویس',
  issued: 'صادر شده',
  partial_paid: 'پرداخت جزئی',
  paid: 'پرداخت شده',
  overdue: 'سررسید گذشته',
  cancelled: 'لغو شده',
};

export const quoteStatusColors: Record<QuoteStatus, 'default' | 'warning' | 'error' | 'success' | 'info'> = {
  draft: 'default',
  sent: 'info',
  accepted: 'success',
  rejected: 'error',
  expired: 'warning',
  converted: 'success',
};

export const quoteStatusLabels: Record<QuoteStatus, string> = {
  draft: 'پیش‌نویس',
  sent: 'ارسال شده',
  accepted: 'پذیرفته شده',
  rejected: 'رد شده',
  expired: 'منقضی شده',
  converted: 'تبدیل به فاکتور',
};

export const leaveStatusColors: Record<LeaveStatus, 'default' | 'warning' | 'error' | 'success' | 'info'> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'error',
  cancelled: 'default',
};

export const leaveStatusLabels: Record<LeaveStatus, string> = {
  pending: 'در انتظار',
  approved: 'تایید شده',
  rejected: 'رد شده',
  cancelled: 'لغو شده',
};

export const payrollStatusColors: Record<PayrollPeriodStatus, 'default' | 'warning' | 'error' | 'success' | 'info'> = {
  draft: 'default',
  processing: 'warning',
  approved: 'info',
  paid: 'success',
  closed: 'default',
};

export const payrollStatusLabels: Record<PayrollPeriodStatus, string> = {
  draft: 'پیش‌نویس',
  processing: 'در حال پردازش',
  approved: 'تایید شده',
  paid: 'پرداخت شده',
  closed: 'بسته شده',
};

// ─────────────────────────────────────────────────────────────────────────────
// Invoice Calculations
// ─────────────────────────────────────────────────────────────────────────────

export function computeLineTotal(
  quantity: string,
  unitPrice: string,
  discountAmount: string,
  taxPercent: string
): { net: number; tax: number; total: number } {
  const qty = parseFloat(quantity) || 0;
  const price = parseFloat(unitPrice) || 0;
  const disc = parseFloat(discountAmount) || 0;
  const taxPct = parseFloat(taxPercent) || 9;
  
  const base = qty * price;
  const net = base - disc;
  const tax = net * taxPct / 100;
  
  return { net, tax, total: net + tax };
}

export function computeInvoiceTotals(lines: Array<{ quantity: string; unitPrice: string; discountAmount: string; taxPercent: string }>) {
  return lines.reduce(
    (acc, line) => {
      const { net, tax, total } = computeLineTotal(
        line.quantity,
        line.unitPrice,
        line.discountAmount,
        line.taxPercent
      );
      return {
        subtotal: acc.subtotal + net + parseFloat(line.discountAmount || '0'),
        discount: acc.discount + parseFloat(line.discountAmount || '0'),
        tax: acc.tax + tax,
        total: acc.total + total,
      };
    },
    { subtotal: 0, discount: 0, tax: 0, total: 0 }
  );
}