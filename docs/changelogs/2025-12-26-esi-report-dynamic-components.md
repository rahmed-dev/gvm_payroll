# ESI Report - Dynamic Component Configuration

## What Changed
ESI Report now uses the `Report Type` field on Salary Components instead of hard-coded component names.

## Why
- Support multiple companies with different component naming conventions
- Allow flexible component names without code changes
- Eliminate hard-coded dependencies

## Impact
⚠️ **Configuration Required** - Report requires Salary Components to have `Report Type` field set

## Required Configuration

For **each company**, set the `Report Type` field on these Salary Components:

| Component Purpose | Report Type Value | Component Type |
|------------------|-------------------|----------------|
| Basic Salary | `Basic` | Earning |
| ESI Employee Contribution | `ESI Employee` | Deduction |
| ESI Employer Contribution | `ESI Employer` | Earning |

## How to Configure

1. Go to **HR → Payroll → Salary Component**
2. Open each relevant component
3. Set the **Company** field
4. Set the **Report Type** field (new dropdown)
5. Save

## Error Handling
If components aren't configured, the report will show which ones are missing:
```
Following salary components are not configured for company ABC Ltd:
• Basic (Report Type: Basic)
• ESI Employee (Report Type: ESI Employee)
• ESI Employer (Report Type: ESI Employer)
```

## Technical Notes
- Modified: `gvm_payroll/report/esi_report/esi_report.py`
- Added function: `get_component_names_by_report_type(company)`
- Query filters: `custom_company` + `custom_report_type`

---
**Date:** 2025-12-26
