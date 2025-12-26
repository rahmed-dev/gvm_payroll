# Multi-Company Setup Guide

## Overview
GVM Payroll supports multiple companies with different payroll configurations using the `custom_company` field on Salary Components.

## Benefits
- Different component names per company
- Company-specific payroll rules
- Isolated configurations
- Flexible reporting

## Setup Steps

### 1. Company Master
Ensure all companies are created in ERPNext:
- **Setup → Company**
- Create/verify company records

### 2. Salary Components
For each company, create/configure salary components:

1. **Navigate:** HR → Payroll → Salary Component
2. **Create/Edit** component
3. **Set:** Company field (required)
4. **Set:** Report Type field (for reports)
5. **Save**

### 3. Report Configuration
Set Report Type values based on usage:

| Report Type | Used By | Purpose |
|------------|---------|---------|
| Basic | ESI Report, PF Report | Basic salary reference |
| ESI Employee | ESI Report | Employee ESI deduction |
| ESI Employer | ESI Report | Employer ESI contribution |
| PF Employee | PF Report | Employee PF deduction |
| PF Employer | PF Report | Employer PF contribution |

### 4. Verification
Test each company's configuration:
1. Run ESI Report for Company A
2. Run ESI Report for Company B
3. Verify correct components used

## Best Practices

### Naming Convention
Use consistent naming across companies:
```
Pattern: [Component Type] - [Company Abbr]

Examples:
- Basic Salary - ABC
- ESI Employee - ABC
- PF Employer - XYZ
```

### Component Organization
- Keep component names descriptive
- Include company abbreviation
- Group by type (Earnings/Deductions)

### Testing
- Test with sample salary slips
- Verify all reports work per company
- Check totals and calculations

## Common Issues

**Issue:** Wrong component used in report
- **Cause:** Multiple components with same Report Type
- **Fix:** Ensure only one component per Report Type per company

**Issue:** Report shows no data
- **Cause:** Components not linked to company
- **Fix:** Set Company field on all components

**Issue:** Error about missing components
- **Cause:** Report Type field not set
- **Fix:** Configure Report Type on required components
