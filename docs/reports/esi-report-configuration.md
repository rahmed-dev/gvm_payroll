# ESI Report Configuration Guide

## Overview
The ESI Report generates Employee State Insurance contribution details for payroll processing. It uses the `Report Type` field on Salary Components for dynamic component selection.

## Prerequisites
- Custom fields on Salary Component:
  - `custom_company` (Link → Company)
  - `custom_report_type` (Select)

## Configuration Steps

### Step 1: Configure Salary Components

For **each company**, configure these three components:

#### 1. Basic Salary Component
- **Field:** Company = Your Company Name
- **Field:** Report Type = `Basic`
- **Field:** Type = Earning

#### 2. ESI Employee Contribution
- **Field:** Company = Your Company Name
- **Field:** Report Type = `ESI Employee`
- **Field:** Type = Deduction

#### 3. ESI Employer Contribution
- **Field:** Company = Your Company Name
- **Field:** Report Type = `ESI Employer`
- **Field:** Type = Earning

### Step 2: Verify Configuration

1. Go to **Reports → ESI Report**
2. Select Company in filters
3. Select Date Range
4. Click **Run**

### Troubleshooting

#### Error: "Components not configured"
**Issue:** Missing Report Type configuration

**Solution:**
1. Check error message for missing components
2. Go to Salary Component master
3. Set Report Type field for listed components
4. Retry report

#### Error: "No data found"
**Issue:** No salary slips in selected date range

**Solution:**
- Verify date range includes processed salary slips
- Check salary slip status (should be Submitted)
- Verify employees have ESI components in salary structure

## Report Columns

| Column | Source | Description |
|--------|--------|-------------|
| Emp. ID | Salary Slip | Employee code |
| Emp. Name | Salary Slip | Employee full name |
| BASIC | Earnings | Basic salary amount |
| Employee Contribution | Deductions | ESI employee deduction |
| Employer Contribution | Earnings | ESI employer contribution |
| Total | Calculated | Sum of employee + employer contributions |

## Notes
- Basic salary shown for reference only (not included in total)
- Total = Employee Contribution + Employer Contribution
- Report respects company-specific component names
- All amounts in company default currency
