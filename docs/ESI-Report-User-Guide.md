# ESI Report - Complete User Guide

## Overview
The ESI Report generates Employee State Insurance contribution details with support for multiple companies and flexible component naming.

---

## Part 1: Configure Salary Components

### Step 1: Add Report Type to Salary Components

For **each company**, configure the following on Salary Components:

**Go to:** HR → Payroll → Salary Component

#### Required Components (3 per company)

| Component Purpose | Company Field | Report Type Field | Component Type |
|------------------|---------------|-------------------|----------------|
| Basic Salary | Your Company | `Basic` | Earning |
| ESI Employee Contribution | Your Company | `ESI Employee` | Deduction |
| ESI Employer Contribution | Your Company | `ESI Employer` | Earning |

### Step 2: Save Each Component

After setting the fields, click **Save** on each Salary Component.

---

## Part 2: Run the Report

### How to Run

1. **Go to:** Reports → ESI Report
2. **Select Filters:**
   - Company (required)
   - From Date
   - To Date
   - Employee (optional)
   - Department (optional)
3. **Click:** Run

### Report Columns

| Column | Description |
|--------|-------------|
| Emp. ID | Employee code |
| Emp. Name | Employee full name |
| Gross | Basic salary amount |
| Employee Contribution | ESI deducted from employee |
| Employer Contribution | ESI paid by employer |
| Total | Sum of employee + employer contributions |

---

### Part 3: Test Print

1. Click **Save**
2. Go to **Reports → ESI Report**
3. Run report with filters
4. Click **Print** → Select `ESI Report - Professional`
5. Verify layout and data

---

## Troubleshooting

### Issue: Report shows error "Components not configured"

**Solution:**
1. Check error message for which components are missing
2. Go to Salary Component master
3. Set the **Report Type** field:
   - Basic Salary → `Basic`
   - ESI Employee → `ESI Employee`
   - ESI Employer → `ESI Employer`
4. Set the **Company** field to your company
5. Save and retry

### Issue: Print format shows template code as text

**Solution:**
- Verify **Print Format Type** = `JS` (not Jinja)
- Verify **For** = `Report` (not DocType)

### Issue: No data in report

**Solution:**
- Verify date range includes salary slips
- Check salary slips are Submitted (not Draft)
- Verify employees have ESI components in their salary structure

### Issue: Numbers not formatted correctly

**Solution:**
- The print format uses Indian locale (₹ 1,23,456.78)
- This is correct for Indian compliance
- No changes needed

---

## Multi-Company Setup

### For Each Company

Repeat the configuration for every company:

1. **Create/Edit Salary Components**
   - Set Company field
   - Set Report Type field
   - Save

2. **Test Each Company**
   - Run ESI Report
   - Verify correct components used
   - Test print format
