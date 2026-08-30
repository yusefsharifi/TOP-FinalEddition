// src/validation/index.ts
// ============================================================================
// Zod Validation Schemas
// ============================================================================

import { z } from 'zod';

// ─────────────────────────────────────────────────────────────────────────────
// Common Validators
// ─────────────────────────────────────────────────────────────────────────────

export const posDecimalStr = z
  .string()
  .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) > 0, 'Must be positive');

export const nonNegDecimalStr = z
  .string()
  .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) >= 0, 'Must be 0 or greater');

export const pctDecimal = z.string().refine((v) => {
  const n = parseFloat(v);
  return n >= 0 && n <= 100;
}, 'Must be 0–100');

// ─────────────────────────────────────────────────────────────────────────────
// Finance Schemas
// ─────────────────────────────────────────────────────────────────────────────

export const journalEntryLineSchema = z
  .object({
    accountId: z.number().int().positive('Account is required'),
    debit: posDecimalStr.optional(),
    credit: posDecimalStr.optional(),
    description: z.string().max(500).optional(),
    costCenter: z.string().max(100).optional(),
  })
  .refine(
    (data) => (data.debit != null) !== (data.credit != null),
    { message: 'Each line must have either debit OR credit, not both and not neither' }
  );

export const journalEntrySchema = z
  .object({
    entryDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be YYYY-MM-DD'),
    periodId: z.number().int().positive('Fiscal period is required'),
    description: z.string().min(1, 'Description is required').max(500),
    descriptionFa: z.string().max(500).optional(),
    lines: z.array(journalEntryLineSchema).min(2, 'At least 2 lines required'),
  })
  .refine(
    (data) => {
      const totalDr = data.lines.reduce((s, l) => s + parseFloat(l.debit || '0'), 0);
      const totalCr = data.lines.reduce((s, l) => s + parseFloat(l.credit || '0'), 0);
      return Math.abs(totalDr - totalCr) < 0.0001;
    },
    {
      message: 'Journal entry must balance: total debits must equal total credits (بدهکارها = بستانکارها)',
      path: ['lines'],
    }
  );

// ─────────────────────────────────────────────────────────────────────────────
// Inventory Schemas
// ─────────────────────────────────────────────────────────────────────────────

const skuRegex = /^[A-Z0-9\-]{3,50}$/;

export const createItemSchema = z
  .object({
    sku: z
      .string()
      .optional()
      .transform((v) => v?.toUpperCase())
      .refine((v) => !v || skuRegex.test(v), {
        message: 'SKU: 3-50 uppercase letters, digits, or hyphens (e.g. WIDGET-001)',
      }),
    name: z.string().min(1, 'Name is required').max(200),
    description: z.string().max(2000).optional(),
    unit_of_measure: z.string().min(1).max(20),
    category_id: z.number().int().positive().optional(),
    default_supplier_id: z.number().int().positive().optional(),
    standard_cost: nonNegDecimalStr.default('0.0000'),
    selling_price: nonNegDecimalStr.optional(),
    global_reorder_point: nonNegDecimalStr.default('0.0000'),
    global_max_stock: nonNegDecimalStr.optional(),
    lead_time_days: z.number().int().min(0).default(0),
    allow_negative_stock: z.boolean().default(false),
  })
  .refine(
    (data) =>
      !data.global_max_stock ||
      parseFloat(data.global_max_stock) > parseFloat(data.global_reorder_point),
    {
      message: 'Max stock must be greater than reorder point',
      path: ['global_max_stock'],
    }
  );

export const inboundMovementSchema = z.object({
  item_id: z.number().int().positive(),
  to_location_id: z.number().int().positive(),
  quantity: posDecimalStr,
  unit_cost: nonNegDecimalStr.optional(),
  supplier_id: z.number().int().positive().optional(),
  reason: z.string().max(500).optional(),
  external_reference: z.string().max(100).optional(),
});

export const outboundMovementSchema = z.object({
  item_id: z.number().int().positive(),
  from_location_id: z.number().int().positive(),
  quantity: posDecimalStr,
  reason: z.string().max(500).optional(),
  external_reference: z.string().max(100).optional(),
});

export const stockTransferSchema = z
  .object({
    item_id: z.number().int().positive(),
    from_location_id: z.number().int().positive(),
    to_location_id: z.number().int().positive(),
    quantity: posDecimalStr,
    reason: z.string().max(500).optional(),
  })
  .refine((data) => data.from_location_id !== data.to_location_id, {
    message: 'Source and destination locations must be different',
    path: ['to_location_id'],
  });

export const stockAdjustSchema = z
  .object({
    item_id: z.number().int().positive(),
    location_id: z.number().int().positive(),
    new_quantity: nonNegDecimalStr.optional(),
    quantity_delta: z
      .string()
      .refine((v) => !isNaN(parseFloat(v)), { message: 'Must be a number' })
      .optional(),
    reason: z.string().min(3, 'Reason is required (min 3 chars)').max(500),
    notes: z.string().max(1000).optional(),
  })
  .refine((data) => !!data.new_quantity !== !!data.quantity_delta, {
    message: 'Provide either new_quantity OR quantity_delta, not both (and not neither)',
  });

// ─────────────────────────────────────────────────────────────────────────────
// Sales Schemas
// ─────────────────────────────────────────────────────────────────────────────

export const invoiceLineSchema = z.object({
  itemId: z.number().int().positive(),
  description: z.string().min(1).max(500),
  quantity: posDecimalStr,
  unitPrice: nonNegDecimalStr,
  discountAmount: nonNegDecimalStr.default('0'),
  taxPercent: pctDecimal.default('9'),
});

export const createInvoiceSchema = z.object({
  customerId: z.number().int().positive('Customer is required'),
  draftDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  dueDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  notes: z.string().max(2000).optional(),
  lines: z.array(invoiceLineSchema).min(1, 'At least one line required'),
});

export const receivePaymentSchema = z.object({
  customerId: z.number().int().positive(),
  invoiceId: z.number().int().positive().optional(),
  paymentDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  amount: posDecimalStr,
  method: z.enum(['cash', 'check', 'bank_transfer', 'card', 'credit_note']),
  referenceNumber: z.string().max(100).optional(),
});

// ─────────────────────────────────────────────────────────────────────────────
// HR Schemas
// ─────────────────────────────────────────────────────────────────────────────

export const employeeSchema = z.object({
  employeeCode: z.string().min(1).max(20),
  firstName: z.string().min(1).max(100),
  lastName: z.string().min(1).max(100),
  firstNameFa: z.string().max(100).optional(),
  lastNameFa: z.string().max(100).optional(),
  nationalId: z.string().length(10, 'National ID must be 10 digits'),
  birthDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  gender: z.enum(['male', 'female']),
  maritalStatus: z.enum(['single', 'married', 'divorced', 'widowed']),
  departmentId: z.number().int().positive().optional(),
  jobTitle: z.string().max(100).optional(),
  employmentType: z.enum(['full_time', 'part_time', 'contract', 'intern']),
  joinDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  baseSalary: nonNegDecimalStr,
  salaryBankAccount: z.string().max(50).optional(),
  bankName: z.string().max(50).optional(),
  insuranceExempt: z.boolean().default(false),
  taxExempt: z.boolean().default(false),
  childrenCount: z.number().int().min(0).default(0),
});

export const leaveRequestSchema = z.object({
  employeeId: z.number().int().positive(),
  leaveType: z.enum(['annual', 'sick', 'unpaid', 'marriage', 'bereavement', 'maternity', 'paternity', 'hajj', 'other']),
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  daysRequested: z.number().int().positive(),
});

// Type exports
export type JournalEntryFormData = z.infer<typeof journalEntrySchema>;
export type CreateItemFormData = z.infer<typeof createItemSchema>;
export type InboundMovementFormData = z.infer<typeof inboundMovementSchema>;
export type OutboundMovementFormData = z.infer<typeof outboundMovementSchema>;
export type StockTransferFormData = z.infer<typeof stockTransferSchema>;
export type StockAdjustFormData = z.infer<typeof stockAdjustSchema>;
export type CreateInvoiceFormData = z.infer<typeof createInvoiceSchema>;
export type ReceivePaymentFormData = z.infer<typeof receivePaymentSchema>;
export type EmployeeFormData = z.infer<typeof employeeSchema>;
export type LeaveRequestFormData = z.infer<typeof leaveRequestSchema>;