# Copyright (c) 2025, GVM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def execute(filters=None):
	if not filters:
		filters = {}

	# Get salary slips based on filters
	salary_slips = get_salary_slips(filters)
	if not salary_slips:
		return [], []

	# Get salary component details grouped by report type
	component_map = get_component_by_report_type(salary_slips)

	# Build columns
	columns = get_columns()

	# Build data rows
	data = []
	for ss in salary_slips:
		row = {
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"designation": ss.designation,
			"total_working_days": ss.total_working_days,
			"payment_days": ss.payment_days,
			"leave_without_pay": ss.leave_without_pay,
		}

		# Get component values for this salary slip
		slip_components = component_map.get(ss.name, {})

		# Add earning components based on report_type
		row["basic_salary"] = slip_components.get("Basic", 0)
		row["fda"] = slip_components.get("FDA", 0)
		row["vda"] = slip_components.get("VDA", 0)
		row["basic_fda_vda"] = row["basic_salary"] + row["fda"] + row["vda"]

		# Add other earning components (you can add more report_types as needed)
		row["hra"] = slip_components.get("HRA", 0)
		row["consolidated_allowance"] = slip_components.get("Consolidated Allowance", 0)
		row["ap"] = slip_components.get("AP", 0)
		row["conveyance_allowance"] = slip_components.get("Conveyance Allowance", 0)

		# Add gross pay
		row["gross_pay"] = flt(ss.gross_pay)

		# Add arrear
		row["arrear"] = slip_components.get("Arrear", 0)

		# Add deduction components based on report_type
		row["lic"] = slip_components.get("LIC", 0)
		row["house_rent"] = slip_components.get("House Rent", 0)
		row["tds"] = slip_components.get("TDS", 0)
		row["prof_tax"] = slip_components.get("Prof Tax", 0)
		row["loans_against_salary"] = slip_components.get("Loan Deduction", 0)
		row["employee_epf"] = slip_components.get("PF Employee", 0)
		row["employee_esic"] = slip_components.get("ESI Employee", 0)

		# Add totals
		row["total_deduction"] = flt(ss.total_deduction) + flt(ss.total_loan_repayment)
		row["net_pay"] = flt(ss.net_pay)

		data.append(row)

	return columns, data


def get_columns():
	"""Build fixed column definitions based on report_type"""
	columns = [
		# Employee info columns
		{
			"label": _("Emp ID"),
			"fieldname": "employee",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 110,
		},
		{
			"label": _("Work Day"),
			"fieldname": "total_working_days",
			"fieldtype": "Float",
			"width": 70,
		},
		{
			"label": _("Wages Day"),
			"fieldname": "payment_days",
			"fieldtype": "Float",
			"width": 75,
		},
		{
			"label": _("LWOP"),
			"fieldname": "leave_without_pay",
			"fieldtype": "Float",
			"width": 60,
		},

		# Earning components based on report_type
		{
			"label": _("Basic Salary"),
			"fieldname": "basic_salary",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"label": _("FDA"),
			"fieldname": "fda",
			"fieldtype": "Currency",
			"width": 90,
		},
		{
			"label": _("VDA"),
			"fieldname": "vda",
			"fieldtype": "Currency",
			"width": 90,
		},
		{
			"label": _("Basic + FDA + VDA"),
			"fieldname": "basic_fda_vda",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("HRA"),
			"fieldname": "hra",
			"fieldtype": "Currency",
			"width": 90,
		},
		{
			"label": _("Consolidated Allowance"),
			"fieldname": "consolidated_allowance",
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"label": _("AP"),
			"fieldname": "ap",
			"fieldtype": "Currency",
			"width": 80,
		},
		{
			"label": _("Conveyance Allowance"),
			"fieldname": "conveyance_allowance",
			"fieldtype": "Currency",
			"width": 110,
		},

		# Gross pay
		{
			"label": _("Gross"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"width": 110,
		},

		# Arrear
		{
			"label": _("Arrear"),
			"fieldname": "arrear",
			"fieldtype": "Currency",
			"width": 90,
		},

		# Deduction components based on report_type
		{
			"label": _("LIC"),
			"fieldname": "lic",
			"fieldtype": "Currency",
			"width": 90,
		},
		{
			"label": _("House Rent"),
			"fieldname": "house_rent",
			"fieldtype": "Currency",
			"width": 90,
		},
		{
			"label": _("TDS"),
			"fieldname": "tds",
			"fieldtype": "Currency",
			"width": 80,
		},
		{
			"label": _("Prof. Tax"),
			"fieldname": "prof_tax",
			"fieldtype": "Currency",
			"width": 80,
		},
		{
			"label": _("Loans Against Salary"),
			"fieldname": "loans_against_salary",
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"label": _("Employee EPF"),
			"fieldname": "employee_epf",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"label": _("Employee ESIC"),
			"fieldname": "employee_esic",
			"fieldtype": "Currency",
			"width": 100,
		},

		# Totals
		{
			"label": _("Total Deduction"),
			"fieldname": "total_deduction",
			"fieldtype": "Currency",
			"width": 110,
		},
		{
			"label": _("Net Salary"),
			"fieldname": "net_pay",
			"fieldtype": "Currency",
			"width": 110,
		},
	]

	return columns


def get_salary_slips(filters):
	"""Fetch salary slips based on filters"""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	# Apply filters
	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters.get("from_date"))

	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters.get("to_date"))

	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))

	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))

	if filters.get("department"):
		query = query.where(salary_slip.department == filters["department"])

	if filters.get("designation"):
		query = query.where(salary_slip.designation == filters["designation"])

	if filters.get("branch"):
		query = query.where(salary_slip.branch == filters["branch"])

	salary_slips = query.run(as_dict=1)

	return salary_slips or []


def get_component_by_report_type(salary_slips):
	"""Get salary components grouped by custom_report_type for each salary slip"""
	salary_slip_names = [ss.name for ss in salary_slips]

	if not salary_slip_names:
		return {}

	# Query to get salary detail with component report type
	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.join(salary_component)
		.on(salary_detail.salary_component == salary_component.name)
		.where(
			(salary_detail.parent.isin(salary_slip_names))
			& (salary_component.custom_internal_component != 1)
		)
		.select(
			salary_detail.parent,
			salary_component.custom_report_type,
			salary_detail.salary_component,
			salary_detail.amount,
		)
	).run(as_dict=1)

	# Build map: {salary_slip_name: {report_type: total_amount}}
	component_map = {}

	for d in result:
		slip_name = d.parent

		# Use custom_report_type, fallback to component name if not set
		report_type = d.custom_report_type or d.salary_component

		amount = flt(d.amount)

		if slip_name not in component_map:
			component_map[slip_name] = {}

		if report_type not in component_map[slip_name]:
			component_map[slip_name][report_type] = 0

		component_map[slip_name][report_type] += amount

	return component_map
