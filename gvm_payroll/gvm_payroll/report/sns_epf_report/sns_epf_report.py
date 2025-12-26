# Copyright (c) 2025, Samuael Ketema and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")


def execute(filters=None):
	if not filters:
		filters = {}

	company = filters.get("company")
	if not company:
		frappe.throw(_("Company is required"))

	salary_slips = get_salary_slips(filters)
	if not salary_slips:
		return [], []

	# Fetch earnings and deductions separately
	ss_earning_map = get_salary_slip_details(salary_slips, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, "deductions")

	# Get component names dynamically based on company and custom_report_type
	component_names = get_component_names_by_report_type(company)

	# PF Wages components (Basic + VDA + FDA)
	BASIC_COMPONENT = component_names.get("basic")
	VDA_COMPONENT = component_names.get("vda")
	FDA_COMPONENT = component_names.get("fda")

	# Other components
	PF_EMPLOYEE_COMPONENT = component_names.get("pf_employee")
	PF_EMPLOYER_COMPONENT = component_names.get("pf_employer")
	PENSION_COMPONENT = component_names.get("pension")

	# Validate required components are configured
	missing_components = []
	if not BASIC_COMPONENT:
		missing_components.append("Basic (Report Type: Basic)")
	if not PF_EMPLOYEE_COMPONENT:
		missing_components.append("PF Employee Share (Report Type: PF Employee)")
	if not PF_EMPLOYER_COMPONENT:
		missing_components.append("PF Employer Share (Report Type: PF Employer)")
	if not PENSION_COMPONENT:
		missing_components.append("Pension Contribution (Report Type: Pension)")

	if missing_components:
		frappe.throw(_(
			"Following salary components are not configured for company {0}:<br><br>{1}<br><br>"
			"Please set 'Report Type' field in Salary Components for this company."
		).format(company, "<br>".join(f"• {comp}" for comp in missing_components)))

	columns = get_columns()

	data = []
	total_pf_wages = 0.0
	total_employee_share = 0.0
	total_employer_share = 0.0
	total_pension = 0.0

	for idx, ss in enumerate(salary_slips, start=1):

		# PF Wages = Basic + VDA + FDA (from earnings)
		basic_amount = flt(ss_earning_map.get(ss.name, {}).get(BASIC_COMPONENT, 0))
		vda_amount = flt(ss_earning_map.get(ss.name, {}).get(VDA_COMPONENT, 0)) if VDA_COMPONENT else 0
		fda_amount = flt(ss_earning_map.get(ss.name, {}).get(FDA_COMPONENT, 0)) if FDA_COMPONENT else 0

		pf_wages = flt(basic_amount + vda_amount + fda_amount, 2)

		# Employee Share (from deductions)
		employee_share = flt(
			ss_ded_map.get(ss.name, {}).get(PF_EMPLOYEE_COMPONENT, 0)
		)

		# Employer Share (from earnings)
		employer_share = flt(
			ss_earning_map.get(ss.name, {}).get(PF_EMPLOYER_COMPONENT, 0)
		)

		# Pension Contribution (from earnings or deductions - check both)
		pension_contribution = flt(
			ss_earning_map.get(ss.name, {}).get(PENSION_COMPONENT, 0) or
			ss_ded_map.get(ss.name, {}).get(PENSION_COMPONENT, 0)
		)

		row = frappe._dict({
			"idx": idx,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"pf_wages": pf_wages,
			"employee_share": employee_share,
			"employer_share": employer_share,
			"pension_contribution": pension_contribution,
		})

		data.append(row)

		# Accumulate totals
		total_pf_wages += pf_wages
		total_employee_share += employee_share
		total_employer_share += employer_share
		total_pension += pension_contribution

	# Calculate summary amounts
	if data:
		# Employee Provident Fund A/c I = Employee Share + Employer Share
		epf_account_1 = flt(total_employee_share + total_employer_share, 2)

		# Employee Pension Fund A/C no 10 = Total Pension
		pension_fund = flt(total_pension, 2)

		# Administrative charges A/C no II = 0.5% of total PF Wages
		admin_charges = flt(total_pf_wages * 0.005, 2)

		# E.D.L.I A/c no 21 = 0.5% of total PF Wages
		edli = flt(total_pf_wages * 0.005, 2)

		# TOTAL = EPF A/c I + Pension Fund + Admin Charges + EDLI
		grand_total = flt(epf_account_1 + pension_fund + admin_charges + edli, 2)

		# Summary metadata (for print format)
		data[0]._meta = {
			"total_pf_wages": total_pf_wages,
			"total_employee_share": total_employee_share,
			"total_employer_share": total_employer_share,
			"total_pension": total_pension,
			"employee_count": len(data),
			"company": company,
			"month": filters.get("month") or "",
			"year": filters.get("year") or "",
			# Summary calculations
			"epf_account_1": epf_account_1,
			"pension_fund": pension_fund,
			"admin_charges": admin_charges,
			"edli": edli,
			"grand_total": grand_total,
		}

		if not data[0]._meta["month"] and filters.get("from_date"):
			from_date = getdate(filters["from_date"])
			data[0]._meta["month"] = formatdate(from_date, "MMMM")
			data[0]._meta["year"] = from_date.year

	return columns, data


def get_columns():
	return [
		{"label": _("SL"), "fieldname": "idx", "fieldtype": "Int", "width": 50},
		{"label": _("Emp. ID"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
		{"label": _("Emp. Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
		{"label": _("PF Wages"), "fieldname": "pf_wages", "fieldtype": "Currency", "width": 120},
		{"label": _("Employee Share"), "fieldname": "employee_share", "fieldtype": "Currency", "width": 130},
		{"label": _("Employer Share"), "fieldname": "employer_share", "fieldtype": "Currency", "width": 130},
		{"label": _("Pension Contribution"), "fieldname": "pension_contribution", "fieldtype": "Currency", "width": 150},
	]


def get_salary_slips(filters):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])
	else:
		query = query.where(salary_slip.docstatus == 1)

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


def get_component_names_by_report_type(company):
	"""
	Fetch salary component names based on custom_report_type field.
	Returns dict with component names for Basic, VDA, FDA, PF Employee, PF Employer, and Pension.
	"""
	components = frappe.get_all(
		"Salary Component",
		filters={
			"custom_company": company,
			"custom_report_type": ["in", ["Basic", "VDA", "FDA", "PF Employee", "PF Employer", "Pension"]]
		},
		fields=["name", "custom_report_type"]
	)

	component_map = {}
	for comp in components:
		report_type = comp.custom_report_type
		if report_type == "Basic":
			component_map["basic"] = comp.name
		elif report_type == "VDA":
			component_map["vda"] = comp.name
		elif report_type == "FDA":
			component_map["fda"] = comp.name
		elif report_type == "PF Employee":
			component_map["pf_employee"] = comp.name
		elif report_type == "PF Employer":
			component_map["pf_employer"] = comp.name
		elif report_type == "Pension":
			component_map["pension"] = comp.name

	return component_map
