import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate
from gvm_payroll.gvm_payroll.report.report_utils import (
	get_internal_salary_details,
	get_salary_slip_details
)

salary_slip = frappe.qb.DocType("Salary Slip")


def execute(filters=None):
	if not filters:
		filters = {}

	company = filters.get("company")
	if not company:
		frappe.throw(_("Company is required"))

	salary_slips = get_salary_slips(filters)
	if not salary_slips:
		return [], []

	# Fetch earnings, deductions, and internal salary details separately
	ss_earning_map = get_salary_slip_details(salary_slips, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, "deductions")
	ss_internal_map = get_internal_salary_details(salary_slips)

	# Get component names dynamically based on company and custom_report_type
	component_names = get_component_names_by_report_type(company)
	BASIC_COMPONENT = component_names.get("basic")
	ESI_EMPLOYEE_COMPONENT = component_names.get("esi_employee")
	ESI_EMPLOYER_COMPONENT = component_names.get("esi_employer")

	# Validate all required components are configured
	missing_components = []
	if not BASIC_COMPONENT:
		missing_components.append("Basic (Report Type: Basic)")
	if not ESI_EMPLOYEE_COMPONENT:
		missing_components.append("ESI Employee (Report Type: ESI Employee)")
	if not ESI_EMPLOYER_COMPONENT:
		missing_components.append("ESI Employer (Report Type: ESI Employer)")

	if missing_components:
		frappe.throw(_(
			"Following salary components are not configured for company {0}:<br><br>{1}<br><br>"
			"Please set 'Report Type' field in Salary Components for this company."
		).format(company, "<br>".join(f"• {comp}" for comp in missing_components)))

	columns = get_columns()

	data = []
	total_basic = 0.0
	total_esi_employee = 0.0
	total_esi_employer = 0.0
	total_all = 0.0

	for idx, ss in enumerate(salary_slips, start=1):

		# Basic Salary (from earnings or internal salary details)
		basic_amount = flt(
			ss_earning_map.get(ss.name, {}).get(BASIC_COMPONENT, 0) or
			ss_internal_map.get(ss.name, {}).get(BASIC_COMPONENT, 0)
		)

		# ESI Employee Contribution (from deductions or internal salary details)
		esi_employee_amount = flt(
			ss_ded_map.get(ss.name, {}).get(ESI_EMPLOYEE_COMPONENT, 0) or
			ss_internal_map.get(ss.name, {}).get(ESI_EMPLOYEE_COMPONENT, 0)
		)

		# ESI Employer Contribution (from earnings or internal salary details)
		esi_employer_amount = flt(
			ss_earning_map.get(ss.name, {}).get(ESI_EMPLOYER_COMPONENT, 0) or
			ss_internal_map.get(ss.name, {}).get(ESI_EMPLOYER_COMPONENT, 0)
		)

		# TOTAL = ESI Employee + ESI Employer (Basic excluded)
		total_amount = esi_employee_amount + esi_employer_amount

		row = frappe._dict({
			"idx": idx,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"basic_salary": basic_amount,
			"esi_employee_contribution": esi_employee_amount,
			"esi_employer_contribution": esi_employer_amount,
			"total": total_amount,
		})

		data.append(row)

		# Accumulate totals
		total_basic += basic_amount
		total_esi_employee += esi_employee_amount
		total_esi_employer += esi_employer_amount
		total_all += total_amount

	# Summary metadata (for print format)
	if data:
		data[0]._meta = {
			"total_basic": total_basic,
			"total_esi_employee": total_esi_employee,
			"total_esi_employer": total_esi_employer,
			"total_all": total_all,
			"employee_count": len(data),
			"company": company,
			"month": filters.get("month") or "",
			"year": filters.get("year") or "",
		}

		if not data[0]._meta["month"] and filters.get("from_date"):
			from_date = getdate(filters["from_date"])
			data[0]._meta["month"] = formatdate(from_date, "MMMM")
			data[0]._meta["year"] = from_date.year

	return columns, data


def get_columns():
	return [
		{"label": _("Emp. ID"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 100},
		{"label": _("Emp. Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
		{"label": _("BASIC"), "fieldname": "basic_salary", "fieldtype": "Currency", "width": 120},
		{"label": _("Employee Contribution"), "fieldname": "esi_employee_contribution", "fieldtype": "Currency", "width": 150},
		{"label": _("Employer Contribution"), "fieldname": "esi_employer_contribution", "fieldtype": "Currency", "width": 150},
		{"label": _("Total"), "fieldname": "total", "fieldtype": "Currency", "width": 120},
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




def get_component_names_by_report_type(company):
	"""
	Fetch salary component names based on custom_report_type field.
	Returns dict with component names for Basic, ESI Employee and ESI Employer.
	"""
	components = frappe.get_all(
		"Salary Component",
		filters={
			"custom_company": company,
			"custom_report_type": ["in", ["Basic", "ESI Employee", "ESI Employer"]]
		},
		fields=["name", "custom_report_type"]
	)

	component_map = {}
	for comp in components:
		if comp.custom_report_type == "Basic":
			component_map["basic"] = comp.name
		elif comp.custom_report_type == "ESI Employee":
			component_map["esi_employee"] = comp.name
		elif comp.custom_report_type == "ESI Employer":
			component_map["esi_employer"] = comp.name

	return component_map
