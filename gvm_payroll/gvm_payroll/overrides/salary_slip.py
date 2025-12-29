# Copyright (c) 2025, Samuael Ketema and contributors
# For license information, please see license.txt

import frappe


def split_internal_components(doc, method=None):
	"""
	Move salary components marked as 'Internal Component' to a separate table.

	Runs on before_save hook - after Frappe's calculation, before database save.
	This ensures calculations are done normally, but components are organized
	into visible and internal tables.

	Components with custom_internal_component = 1 will be moved from:
	- doc.earnings → doc.custom_internal_salary_details
	- doc.deductions → doc.custom_internal_salary_details
	"""
	# Performance optimization: Skip if nothing changed
	# BUT always run during submit to ensure components stay split
	if doc.docstatus == 0:  # Only optimize for draft saves
		if not (doc.has_value_changed("earnings") or doc.has_value_changed("deductions")):
			return

	# Clear existing internal components to avoid duplicates
	doc.custom_internal_salary_details = []

	# Process earnings - collect items to move
	items_to_move = []
	for earning in list(doc.earnings):  # Create copy to safely iterate
		if should_move_to_internal(earning.salary_component):
			items_to_move.append(earning)

	# Move items to internal table and remove from earnings
	for item in items_to_move:
		add_to_internal_table(doc, item, component_type="Earning")
		doc.earnings.remove(item)  # Remove in-place instead of replacing list

	# Process deductions - collect items to move
	items_to_move = []
	for deduction in list(doc.deductions):  # Create copy to safely iterate
		if should_move_to_internal(deduction.salary_component):
			items_to_move.append(deduction)

	# Move items to internal table and remove from deductions
	for item in items_to_move:
		add_to_internal_table(doc, item, component_type="Deduction")
		doc.deductions.remove(item)  # Remove in-place instead of replacing list

	# Calculate total of internal components
	calculate_internal_total(doc)


def should_move_to_internal(salary_component_name):
	"""
	Check if a salary component should be moved to internal table.

	Args:
		salary_component_name (str): Name of the Salary Component

	Returns:
		bool: True if component has custom_internal_component = 1
	"""
	try:
		# Use get_cached_value for single field lookup (more efficient than get_cached_doc)
		is_internal = frappe.get_cached_value(
			"Salary Component", salary_component_name, "custom_internal_component"
		)
		return is_internal == 1
	except Exception as e:
		# Log error for debugging
		frappe.log_error(
			message=f"Failed to check internal component flag for '{salary_component_name}': {str(e)}",
			title="Salary Slip - Internal Component Check Failed",
		)
		return False


def add_to_internal_table(doc, component_row, component_type):
	"""
	Add a salary component to the internal salary details table.

	Args:
		doc: Salary Slip document
		component_row: The earning/deduction row object
		component_type (str): "Earning" or "Deduction"
	"""
	doc.append(
		"custom_internal_salary_details",
		{
			"salary_component": component_row.salary_component,
			"abbr": component_row.get("abbr"),
			"amount": component_row.amount,
			"default_amount": component_row.get("default_amount"),
			"additional_amount": component_row.get("additional_amount"),
			"type": component_type,
			# Copy any other fields that exist in both child tables
			"depends_on_payment_days": component_row.get("depends_on_payment_days"),
			"do_not_include_in_total": component_row.get("do_not_include_in_total"),
		},
	)


def calculate_internal_total(doc):
	"""
	Calculate the total of all internal salary components and set it to custom_gross_internal_payable.

	Args:
		doc: Salary Slip document
	"""
	total = 0.0

	# Sum all amounts in internal salary details table
	if doc.custom_internal_salary_details:
		for row in doc.custom_internal_salary_details:
			if row.amount:
				total += row.amount

	# Set the total to the custom field
	doc.custom_gross_internal_payable = total


def calculate_unpaid_days(doc, method=None):
	"""
	Calculate total unpaid days for the employee from Unpaid Days doctype.

	Runs on before_save hook - after Frappe's standard salary slip calculations.
	Queries all submitted Unpaid Days documents where payroll_date falls between
	the salary slip's start_date and end_date, then sums the days for this employee.

	Args:
		doc: Salary Slip document
		method: Hook method name (optional)
	"""
	# Skip if required fields are missing
	if not doc.employee or not doc.start_date or not doc.end_date:
		doc.custom_unpaid_days = 0.0
		return

	# Query all submitted Unpaid Days documents within salary slip date range
	unpaid_days_docs = frappe.get_all(
		"Unpaid Days",
		filters={
			"docstatus": 1,  # Only submitted documents
			"payroll_date": ["between", [doc.start_date, doc.end_date]]
		},
		pluck="name"
	)

	# If no unpaid days documents found, set to 0
	if not unpaid_days_docs:
		doc.custom_unpaid_days = 0.0
		return

	# Sum all unpaid days for this employee from the details table
	total_unpaid_days = 0.0

	for unpaid_doc_name in unpaid_days_docs:
		# Get all detail rows for this employee from this Unpaid Days document
		employee_unpaid_days = frappe.get_all(
			"Unpaid Days Detail",
			filters={
				"parent": unpaid_doc_name,
				"parenttype": "Unpaid Days",
				"employee": doc.employee
			},
			fields=["days"]
		)

		# Sum the days
		for row in employee_unpaid_days:
			if row.days:
				total_unpaid_days += row.days

	# Update the custom field
	doc.custom_unpaid_days = total_unpaid_days
