import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate
from datetime import datetime, timedelta
import calendar

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")


def execute(filters=None):
	if not filters:
		filters = {}

	company = filters.get("company")
	if not company:
		frappe.throw(_("Company is required"))

	fiscal_year = filters.get("fiscal_year")
	if not fiscal_year:
		frappe.throw(_("Fiscal Year is required"))

	# Get fiscal year dates
	fy = frappe.get_doc("Fiscal Year", fiscal_year)
	# Financial year in India is April to March
	# Assuming fiscal year is set correctly (April to March)
	from_date = fy.year_start_date
	to_date = fy.year_end_date

	# Get all months from April to March
	months = get_financial_year_months(from_date, to_date)
	
	# Store months in filters for HTML template
	filters["_months"] = months

	salary_slips = get_salary_slips(filters, from_date, to_date)
	if not salary_slips:
		return [], []

	# Get salary slip details for earnings and deductions
	ss_earning_map = get_salary_slip_details(salary_slips, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, "deductions")

	# Group salary slips by employee
	employee_slips = {}
	for ss in salary_slips:
		if ss.employee not in employee_slips:
			employee_slips[ss.employee] = []
		employee_slips[ss.employee].append(ss)

	columns = get_columns(months)

	data = []

	for employee, slips in employee_slips.items():
		# Get employee name
		employee_name = slips[0].employee_name if slips else ""
		
		# Initialize monthly data
		monthly_data = {}
		for month_key in months.keys():
			monthly_data[month_key] = {
				"basic": 0.0,
				"da": 0.0,
				"fixall": 0.0,
				"ta": 0.0,
				"house_rent": 0.0,
				"grinsur": 0.0,
				"lic": 0.0,
				"mpf": 0.0,
				"current_month_income_tax": 0.0,
			}

		# Process each salary slip
		for ss in slips:
			month_key = get_month_key(ss.start_date)
			if month_key not in monthly_data:
				continue

			earnings_map = ss_earning_map.get(ss.name, {})
			deductions_map = ss_ded_map.get(ss.name, {})

			# Basic
			basic = get_component_amount(earnings_map, ["Basic Salary", "Basic", "BASIC"])
			monthly_data[month_key]["basic"] += basic

			# DA = Dearness Allowences
			da = get_component_amount(earnings_map, ["Dearness Allowences", "Dearness Allowence", "DA", "D.A.", "Dearness"])
			monthly_data[month_key]["da"] += da

			# TA = Travel Allowences
			ta = get_component_amount(earnings_map, ["Travel Allowences", "Travel Allowence", "TA", "T.A.", "Travel"])
			monthly_data[month_key]["ta"] += ta

			# House Rent = House Rent + Water Charges + Garbage Maintainence + Servant Charge + Parking Charge
			# Check both earnings and deductions, only add if component exists
			house_rent_total = 0.0
			
			# House Rent
			house_rent = get_component_amount(earnings_map, ["House Rent", "HRA", "House Rent Allowance"])
			if house_rent == 0:
				house_rent = get_component_amount(deductions_map, ["House Rent", "HRA", "House Rent Allowance"])
			house_rent_total += house_rent
			
			# Water Charges
			water = get_component_amount(earnings_map, ["Water Charges", "Water", "Water Charge"])
			if water == 0:
				water = get_component_amount(deductions_map, ["Water Charges", "Water", "Water Charge"])
			house_rent_total += water
			
			# Garbage Maintainence
			garbage = get_component_amount(earnings_map, ["Garbage Maintainence", "Garbage Maintenance", "Garbage", "Garbage Maintainence"])
			if garbage == 0:
				garbage = get_component_amount(deductions_map, ["Garbage Maintainence", "Garbage Maintenance", "Garbage", "Garbage Maintainence"])
			house_rent_total += garbage
			
			# Servant Charge
			servant = get_component_amount(earnings_map, ["Servant Charge", "Servant", "Servant Charges"])
			if servant == 0:
				servant = get_component_amount(deductions_map, ["Servant Charge", "Servant", "Servant Charges"])
			house_rent_total += servant
			
			# Parking Charge
			parking = get_component_amount(earnings_map, ["Parking Charge", "Parking", "Parking Charges"])
			if parking == 0:
				parking = get_component_amount(deductions_map, ["Parking Charge", "Parking", "Parking Charges"])
			house_rent_total += parking
			
			monthly_data[month_key]["house_rent"] += house_rent_total

			# Grinsur = Group Insurance
			grinsur = get_component_amount(deductions_map, ["Group Insurance", "Group Ins", "Grinsur", "Group Insur"])
			monthly_data[month_key]["grinsur"] += grinsur

			# LIC = LIC
			lic = get_component_amount(deductions_map, ["LIC", "Life Insurance", "Life Insurance Corporation"])
			monthly_data[month_key]["lic"] += lic

			# MPF = Provident Fund - Employee Contribution
			mpf = get_component_amount(deductions_map, [
				"Provident Fund - Employee Contribution",
				"PF - Employee Contribution",
				"PF Employee Contribution",
				"Provident Fund Employee",
			])
			monthly_data[month_key]["mpf"] += mpf

			# Current month income tax
			monthly_data[month_key]["current_month_income_tax"] = flt(ss.current_month_income_tax or 0)

		# FixAll = 40 for all months if we have at least one salary slip
		if slips:
			for month_key in monthly_data.keys():
				monthly_data[month_key]["fixall"] = 40.0

		# Find ANY month with data and copy to all months
		# Use the first month that has any data (prefer one with basic salary)
		source_month = None
		for month_key, month_data in monthly_data.items():
			if month_data["basic"] > 0:
				source_month = month_key
				break
		
		# If no month with basic, find any month with any data
		if not source_month:
			for month_key, month_data in monthly_data.items():
				if (month_data["basic"] > 0 or month_data["da"] > 0 or month_data["ta"] > 0 or
					month_data["house_rent"] > 0 or month_data["grinsur"] > 0 or 
					month_data["lic"] > 0 or month_data["mpf"] > 0):
					source_month = month_key
					break
		
		# If we found a month with data, copy its data to ALL months
		if source_month:
			source_data = monthly_data[source_month]
			# Calculate totals for source month
			source_data["total"] = (
				source_data["basic"] + source_data["da"] + source_data["fixall"] +
				source_data["ta"] + source_data["house_rent"]
			)
			source_data["savings_total"] = (
				source_data["grinsur"] + source_data["lic"] + source_data["mpf"]
			)
			
			# Copy to ALL months (including source month to ensure consistency)
			for month_key in monthly_data.keys():
				monthly_data[month_key]["basic"] = source_data["basic"]
				monthly_data[month_key]["da"] = source_data["da"]
				monthly_data[month_key]["ta"] = source_data["ta"]
				monthly_data[month_key]["house_rent"] = source_data["house_rent"]
				monthly_data[month_key]["grinsur"] = source_data["grinsur"]
				monthly_data[month_key]["lic"] = source_data["lic"]
				monthly_data[month_key]["mpf"] = source_data["mpf"]
				# FixAll is already set to 40 for all
				# Copy monthly totals
				monthly_data[month_key]["total"] = source_data["total"]
				monthly_data[month_key]["savings_total"] = source_data["savings_total"]

		# Calculate totals and summary
		# If we copied data, multiply by 12 (number of months)
		if source_month:
			source_data = monthly_data[source_month]
			total_basic = flt(source_data["basic"] * 12, 2)
			total_da = flt(source_data["da"] * 12, 2)
			total_fixall = flt(source_data["fixall"] * 12, 2)
			total_ta = flt(source_data["ta"] * 12, 2)
			total_house_rent = flt(source_data["house_rent"] * 12, 2)
			total_grinsur = flt(source_data["grinsur"] * 12, 2)
			total_lic = flt(source_data["lic"] * 12, 2)
			total_mpf = flt(source_data["mpf"] * 12, 2)
		else:
			total_basic = sum(m["basic"] for m in monthly_data.values())
			total_da = sum(m["da"] for m in monthly_data.values())
			total_fixall = sum(m["fixall"] for m in monthly_data.values())
			total_ta = sum(m["ta"] for m in monthly_data.values())
			total_house_rent = sum(m["house_rent"] for m in monthly_data.values())
			total_grinsur = sum(m["grinsur"] for m in monthly_data.values())
			total_lic = sum(m["lic"] for m in monthly_data.values())
			total_mpf = sum(m["mpf"] for m in monthly_data.values())

		total_earnings = total_basic + total_da + total_fixall + total_ta + total_house_rent
		
		# Less Std Dedn = 50000 for all
		less_std_dedn = 50000.0
		
		# IncomeSal head = total - less std dedn
		income_sal_head = total_earnings - less_std_dedn

		# Total savings = Grinsur + LIC + MPF
		total_savings = total_grinsur + total_lic + total_mpf

		# Qualifying amount = total savings with limit of 150000
		qualifying_amt = min(total_savings, 150000.0)

		# Taxable income = IncomeSal head - Qualifying amount
		taxable_income = income_sal_head - qualifying_amt

		# Get current month (use source month if we copied data, otherwise find last month with data)
		current_month_key = source_month if source_month else None
		if not current_month_key:
			for month_key in sorted(monthly_data.keys(), reverse=True):
				if monthly_data[month_key]["basic"] > 0:
					current_month_key = month_key
					break

		# Calculate months passed from April to current month
		if current_month_key:
			months_passed = get_months_passed(from_date, current_month_key)
		else:
			months_passed = 12

		# Tax payable = 12 * current_month_income_tax (from source month or last month with data)
		# Get the tax from the source month (the one we found with data)
		if source_month:
			current_month_tax = monthly_data[source_month].get("current_month_income_tax", 0.0)
		elif current_month_key:
			current_month_tax = monthly_data[current_month_key].get("current_month_income_tax", 0.0)
		else:
			current_month_tax = 0.0
		
		tax_payable = flt(current_month_tax * 12, 2)

		# Itax paid = months_passed (from April to current month) * current_month_income_tax
		itax_paid = flt(months_passed * current_month_tax, 2)

		# Bal to pay = tax payable - itax paid
		bal_to_pay = flt(tax_payable - itax_paid, 2)

		# New Mly Dedn = bal to pay / months_passed (if months_passed > 0)
		new_mly_dedn = flt(bal_to_pay / months_passed, 2) if months_passed > 0 else 0.0

		# Build row data
		row = {
			"employee": employee,
			"employee_name": employee_name,
			"total_basic": total_basic,
			"total_da": total_da,
			"total_fixall": total_fixall,
			"total_ta": total_ta,
			"total_house_rent": total_house_rent,
			"total_earnings": total_earnings,
			"less_std_dedn": less_std_dedn,
			"income_sal_head": income_sal_head,
			"total_grinsur": total_grinsur,
			"total_lic": total_lic,
			"total_mpf": total_mpf,
			"total_savings": total_savings,
			"qualifying_amt": qualifying_amt,
			"taxable_income": taxable_income,
			"tax_payable": tax_payable,
			"itax_paid": itax_paid,
			"bal_to_pay": bal_to_pay,
			"new_mly_dedn": new_mly_dedn,
			"_months_data": monthly_data,  # Store monthly data for HTML template
			"_months_keys": list(months.keys()),  # Store month keys in order
		}

		# Add monthly data as separate fields for easier access in HTML
		for month_key, month_label in months.items():
			month_data = monthly_data.get(month_key, {})
			row[f"basic_{month_key}"] = month_data.get("basic", 0.0)
			row[f"da_{month_key}"] = month_data.get("da", 0.0)
			row[f"fixall_{month_key}"] = month_data.get("fixall", 0.0)
			row[f"ta_{month_key}"] = month_data.get("ta", 0.0)
			row[f"house_rent_{month_key}"] = month_data.get("house_rent", 0.0)
			# Use pre-calculated total if available, otherwise calculate
			if "total" in month_data:
				row[f"total_{month_key}"] = month_data.get("total", 0.0)
			else:
				row[f"total_{month_key}"] = (
					month_data.get("basic", 0.0) +
					month_data.get("da", 0.0) +
					month_data.get("fixall", 0.0) +
					month_data.get("ta", 0.0) +
					month_data.get("house_rent", 0.0)
				)
			row[f"grinsur_{month_key}"] = month_data.get("grinsur", 0.0)
			row[f"lic_{month_key}"] = month_data.get("lic", 0.0)
			row[f"mpf_{month_key}"] = month_data.get("mpf", 0.0)
			# Use pre-calculated savings_total if available
			if "savings_total" in month_data:
				row[f"savings_total_{month_key}"] = month_data.get("savings_total", 0.0)
			else:
				row[f"savings_total_{month_key}"] = (
					month_data.get("grinsur", 0.0) +
					month_data.get("lic", 0.0) +
					month_data.get("mpf", 0.0)
				)

		data.append(row)

	return columns, data


def get_component_amount(component_map, component_names):
	"""Get amount for a component, trying multiple name variations."""
	for comp in component_names:
		if comp in component_map:
			return flt(component_map[comp])
		# Try case-insensitive match
		for key in component_map.keys():
			if key.lower() == comp.lower():
				return flt(component_map[key])
			# Try partial match
			if comp.lower() in key.lower() or key.lower() in comp.lower():
				return flt(component_map[key])
	return 0.0


def get_financial_year_months(from_date, to_date):
	"""Get all months from April to March in format YYYYMM."""
	months = {}
	
	# Financial year starts in April
	# Determine the start year
	if from_date.month >= 4:
		start_year = from_date.year
		start_month = from_date.month
	else:
		# If from_date is before April, start from previous year's April
		start_year = from_date.year - 1
		start_month = 4
	
	current = getdate(f"{start_year}-{start_month:02d}-01")
	
	month_num = 0
	while month_num < 12:
		if current > to_date:
			break
		month_key = f"{current.year}{current.month:02d}"
		months[month_key] = month_key  # Use YYYYMM as label
		
		# Move to next month
		if current.month == 12:
			current = current.replace(year=current.year + 1, month=1)
		else:
			current = current.replace(month=current.month + 1)
		month_num += 1
	
	return months


def get_month_key(date):
	"""Convert date to YYYYMM format."""
	if isinstance(date, str):
		date = getdate(date)
	return f"{date.year}{date.month:02d}"


def get_months_passed(from_date, current_month_key):
	"""Calculate months passed from April to current month."""
	if isinstance(from_date, str):
		from_date = getdate(from_date)
	
	# Parse current_month_key (YYYYMM)
	current_year = int(current_month_key[:4])
	current_month = int(current_month_key[4:])
	
	# Financial year starts in April
	# If from_date is April, that's month 1
	# If from_date month < 4, the FY started in previous year's April
	
	fy_start_year = from_date.year
	if from_date.month < 4:
		fy_start_year = from_date.year - 1
	
	# Calculate months
	if current_year == fy_start_year:
		# Same year: April (4) to current_month
		months = current_month - 3  # April=4, so 4-3=1 for April, 5-3=2 for May, etc.
	else:
		# Different year: months from April to Dec (9 months) + months in current year
		months = (12 - 3) + current_month  # 9 months (Apr-Dec) + months in current year
	
	return max(months, 1)


def get_columns(months):
	"""Generate columns for the report."""
	columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 200,
		},
	]

	# Store months in a special field for HTML template
	columns.append({
		"label": _("Months Data"),
		"fieldname": "_months_data",
		"fieldtype": "Data",
		"hidden": 1,
	})

	# Add summary columns (these will be used in the report)
	summary_columns = [
		{"label": _("Total Basic"), "fieldname": "total_basic", "fieldtype": "Currency", "width": 120},
		{"label": _("Total DA"), "fieldname": "total_da", "fieldtype": "Currency", "width": 120},
		{"label": _("Total FixAll"), "fieldname": "total_fixall", "fieldtype": "Currency", "width": 120},
		{"label": _("Total TA"), "fieldname": "total_ta", "fieldtype": "Currency", "width": 120},
		{"label": _("Total House Rent"), "fieldname": "total_house_rent", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Earnings"), "fieldname": "total_earnings", "fieldtype": "Currency", "width": 120},
		{"label": _("Less Std Dedn"), "fieldname": "less_std_dedn", "fieldtype": "Currency", "width": 120},
		{"label": _("IncomeSal head"), "fieldname": "income_sal_head", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Grinsur"), "fieldname": "total_grinsur", "fieldtype": "Currency", "width": 120},
		{"label": _("Total LIC"), "fieldname": "total_lic", "fieldtype": "Currency", "width": 120},
		{"label": _("Total MPF"), "fieldname": "total_mpf", "fieldtype": "Currency", "width": 120},
		{"label": _("Total Savings"), "fieldname": "total_savings", "fieldtype": "Currency", "width": 120},
		{"label": _("Qualifying amt"), "fieldname": "qualifying_amt", "fieldtype": "Currency", "width": 120},
		{"label": _("Taxable income"), "fieldname": "taxable_income", "fieldtype": "Currency", "width": 120},
		{"label": _("Tax payable"), "fieldname": "tax_payable", "fieldtype": "Currency", "width": 120},
		{"label": _("Itax paid"), "fieldname": "itax_paid", "fieldtype": "Currency", "width": 120},
		{"label": _("Bal to pay"), "fieldname": "bal_to_pay", "fieldtype": "Currency", "width": 120},
		{"label": _("New Mly Dedn"), "fieldname": "new_mly_dedn", "fieldtype": "Currency", "width": 120},
	]

	columns.extend(summary_columns)

	return columns


def get_salary_slips(filters, from_date, to_date):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])
	else:
		query = query.where(salary_slip.docstatus == 1)

	query = query.where(salary_slip.start_date >= from_date)
	query = query.where(salary_slip.end_date <= to_date)

	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))

	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))

	return query.run(as_dict=1) or []


def get_salary_slip_details(salary_slips, component_type):
	salary_slips = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where(
			(salary_detail.parent.isin(salary_slips))
			& (salary_detail.parentfield == component_type)
		)
		.select(
			salary_detail.parent,
			salary_detail.salary_component,
			salary_detail.amount,
		)
	).run(as_dict=1)

	ss_map = {}
	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map

