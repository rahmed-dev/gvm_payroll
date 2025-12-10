import frappe


def execute():
	"""Add missing custom field to Payroll Entry"""
	try:
		# Check if field already exists in Custom Field doctype
		field_exists = frappe.db.exists(
			"Custom Field",
			{"dt": "Payroll Entry", "fieldname": "deduct_tax_for_unclaimed_employee_benefits"}
		)
		
		# Also check if field exists in the DocType meta
		if not field_exists:
			meta = frappe.get_meta("Payroll Entry")
			field_exists = meta.has_field("deduct_tax_for_unclaimed_employee_benefits")
		
		if not field_exists:
			custom_field = frappe.get_doc({
				"doctype": "Custom Field",
				"dt": "Payroll Entry",
				"label": "Deduct Tax for Unclaimed Employee Benefits",
				"fieldname": "deduct_tax_for_unclaimed_employee_benefits",
				"fieldtype": "Check",
				"default": "0",
				"insert_after": "deduct_tax_for_unsubmitted_tax_exemption_proof",
			})
			custom_field.insert(ignore_permissions=True)
			frappe.db.commit()
	except frappe.exceptions.ValidationError as e:
		# Field already exists - this is fine, just skip
		if "already exists" in str(e):
			pass
		else:
			raise
	except Exception as e:
		# Log shorter error message to avoid truncation
		frappe.log_error(f"Patch error: {type(e).__name__}", "add_missing_payroll_entry_field")
		# Don't raise - allow migration to continue
