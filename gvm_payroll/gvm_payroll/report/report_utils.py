# Copyright (c) 2025, Samuael Ketema and contributors
# For license information, please see license.txt

"""
Shared utility functions for payroll reports.

This module contains common functions used across multiple reports to avoid code duplication
and ensure consistent behavior.
"""

import frappe
from frappe.utils import flt

# Define DocTypes for query builder
salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
internal_salary_detail = frappe.qb.DocType("Internal Salary Details")


def get_internal_salary_details(
	salary_slips,
	exclude_components=None,
	include_components=None,
	custom_filters=None
):
	"""
	Fetch internal salary details from custom_internal_salary_details table.

	This function retrieves salary components that have been moved to the internal
	salary details table (components marked with custom_internal_component = 1).

	Args:
		salary_slips (list): List of salary slip documents
		exclude_components (list, optional): List of component names to exclude from results.
			Example: ["Bonus", "Commission"]
		include_components (list, optional): Only include these specific components.
			Example: ["PF Employer", "Pension"]
		custom_filters (QB filter, optional): Additional Frappe Query Builder filters.
			Example: (internal_salary_detail.custom_report_type == "PF")

	Returns:
		dict: Map of salary slip name -> component name -> amount
			Example: {
				"SS-0001": {"PF Employer": 1000.0, "Pension": 500.0},
				"SS-0002": {"PF Employer": 1200.0, "Pension": 600.0}
			}

	Usage Examples:
		# Get all internal components (default)
		ss_internal_map = get_internal_salary_details(salary_slips)

		# Exclude specific components
		ss_internal_map = get_internal_salary_details(
			salary_slips,
			exclude_components=["Bonus", "Special Allowance"]
		)

		# Only include specific components
		ss_internal_map = get_internal_salary_details(
			salary_slips,
			include_components=["PF Employer", "Pension"]
		)

		# Custom filter by component property
		ss_internal_map = get_internal_salary_details(
			salary_slips,
			custom_filters=(internal_salary_detail.custom_report_type == "PF")
		)
	"""
	if not salary_slips:
		return {}

	salary_slips_names = [ss.name for ss in salary_slips]

	# Build base query
	query = (
		frappe.qb.from_(salary_slip)
		.join(internal_salary_detail)
		.on(salary_slip.name == internal_salary_detail.parent)
		.where(
			(internal_salary_detail.parent.isin(salary_slips_names))
			& (internal_salary_detail.parenttype == "Salary Slip")
		)
	)

	# Apply optional filters
	if exclude_components:
		query = query.where(internal_salary_detail.salary_component.notin(exclude_components))

	if include_components:
		query = query.where(internal_salary_detail.salary_component.isin(include_components))

	if custom_filters:
		query = query.where(custom_filters)

	# Execute query
	result = query.select(
		internal_salary_detail.parent,
		internal_salary_detail.salary_component,
		internal_salary_detail.amount,
	).run(as_dict=1)

	# Build map: salary_slip -> component -> amount
	ss_map = {}
	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map


def get_salary_slip_details(salary_slips, component_type):
	"""
	Fetch salary details from standard earnings or deductions tables.

	Args:
		salary_slips (list): List of salary slip documents
		component_type (str): Either "earnings" or "deductions"

	Returns:
		dict: Map of salary slip name -> component name -> amount
			Example: {
				"SS-0001": {"Basic": 10000.0, "HRA": 5000.0},
				"SS-0002": {"Basic": 12000.0, "HRA": 6000.0}
			}
	"""
	if not salary_slips:
		return {}

	salary_slips_names = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where(
			(salary_detail.parent.isin(salary_slips_names))
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
