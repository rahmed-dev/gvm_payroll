# ESI Report Print Format - Exact Match

## HTML Code

```html
<div class="esi-report-wrapper">
    <!-- Main Title -->
    <div class="report-main-title">ESI Report</div>

    <!-- Header - Year and Month -->
    {% if (data.length > 0 && data[0]._meta) { %}
        {%
        var meta = data[0]._meta;
        var month = meta.month || "";
        var year = meta.year || "";
        var period = month && year ? month + " " + year : "";
        %}
        <div class="report-header-simple">
            <strong>Year and Month :</strong> {%= period %}
        </div>
    {% } %}

    <!-- Main Table -->
    <table class="esi-simple-table">
        <thead>
            <tr>
                <th>Sl</th>
                <th>Emp. ID</th>
                <th>Emp. Name</th>
                <th>Gross</th>
                <th>Employee Contribution</th>
                <th>Employer Contribution</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for (var i = 0; i < data.length; i++) { %}
                {%
                var row = data[i];
                var sno = i + 1;
                var empId = row.employee || "";
                var empName = row.employee_name || "";
                var gross = parseFloat(row.basic_salary) || 0;
                var esiEmp = parseFloat(row.esi_employee_contribution) || 0;
                var esiEmplr = parseFloat(row.esi_employer_contribution) || 0;
                var total = parseFloat(row.total) || 0;
                %}
                <tr>
                    <td class="text-center">{%= sno %}</td>
                    <td class="text-center">{%= empId %}</td>
                    <td>{%= empName %}</td>
                    <td class="text-right">{%= gross.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</td>
                    <td class="text-right">{%= esiEmp.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</td>
                    <td class="text-right">{%= esiEmplr.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</td>
                    <td class="text-right">{%= total.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</td>
                </tr>
            {% } %}
        </tbody>

        <!-- Totals Footer -->
        {% if (data.length > 0 && data[0]._meta) { %}
            {%
            var meta = data[0]._meta;
            var empCount = meta.employee_count || 0;
            var totalGross = parseFloat(meta.total_basic) || 0;
            var totalEsiEmp = parseFloat(meta.total_esi_employee) || 0;
            var totalEsiEmplr = parseFloat(meta.total_esi_employer) || 0;
            var grandTotal = parseFloat(meta.total_all) || 0;
            %}
            <tfoot>
                <tr class="total-row">
                    <td colspan="3" class="text-left">
                        <strong>Total No of Employees: {%= empCount %}</strong>
                    </td>
                    <td class="text-right">
                        <strong>{%= totalGross.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</strong>
                    </td>
                    <td class="text-right">
                        <strong>{%= totalEsiEmp.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigals: 2}) %}</strong>
                    </td>
                    <td class="text-right">
                        <strong>{%= totalEsiEmplr.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</strong>
                    </td>
                    <td class="text-right">
                        <strong>{%= grandTotal.toLocaleString("en-IN", {minimumFractionDigits: 2, maximumFractionDigits: 2}) %}</strong>
                    </td>
                </tr>
            </tfoot>
        {% } %}
    </table>
</div>
```

---

## CSS Code

```css
/* Wrapper */
.esi-report-wrapper {
    padding: 20px;
    font-family: Arial, sans-serif;
    font-size: 12px;
}

/* Main Title */
.report-main-title {
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Header */
.report-header-simple {
    margin-bottom: 15px;
    font-size: 13px;
}

/* Table */
.esi-simple-table {
    width: 100%;
    border-collapse: collapse;
    border: 2px solid #000;
}

.esi-simple-table th,
.esi-simple-table td {
    border: 1px solid #000;
    padding: 8px 10px;
}

/* Table Header */
.esi-simple-table thead th {
    background-color: #fff;
    color: #000;
    font-weight: bold;
    text-align: center;
    font-size: 11px;
    vertical-align: middle;
    line-height: 1.3;
}

/* Table Body */
.esi-simple-table tbody td {
    font-size: 11px;
    vertical-align: middle;
}

/* Table Footer */
.esi-simple-table tfoot td {
    font-weight: bold;
    background-color: #fff;
    font-size: 11px;
}

/* Text Alignment */
.text-left {
    text-align: left;
}

.text-center {
    text-align: center;
}

.text-right {
    text-align: right;
}

/* Total Row */
.total-row {
    border-top: 2px solid #000;
}

/* Print Optimization */
@media print {
    .esi-report-wrapper {
        padding: 10px;
    }

    .esi-simple-table {
        font-size: 10px;
    }

    .esi-simple-table th,
    .esi-simple-table td {
        padding: 4px 6px;
    }
}
```

---

## Setup Instructions

1. **Create Print Format:**
   - Name: `ESI Report - Simple`
   - For: `Report`
   - Report: `ESI Report`
   - Type: `JS`

2. **Copy HTML** → Paste in HTML field

3. **Copy CSS** → Paste in Custom CSS field

4. **Save and Test**

---

## Key Differences from Previous Version

✅ **Simplified Design** - Black borders on white background
✅ **"Gross" Column** - Instead of "Basic Salary"
✅ **"Year and Month" Header** - Simple text format
✅ **"Total No of Employees"** - In footer left side
✅ **No Colors** - Professional black & white only
✅ **Clean Borders** - All cells have visible borders
✅ **Compact Layout** - Matches your image exactly

---

## Notes

- The "Gross" column currently uses `basic_salary` field from the report
- If your report has a separate gross field, update line with the correct field name
- Number format: Indian locale (1,23,456.78)
