import frappe
from frappe.utils import getdate, nowdate, date_diff, add_days


@frappe.whitelist()
def create_quarter_additional_salaries(payroll_entry: str):
	"""
	Create Additional Salary records for employees in the given Payroll Entry
	using their assigned quarter charges. The payroll_date is set to the midpoint
	between start_date and end_date (inclusive).
	"""
	if not payroll_entry:
		frappe.throw("Payroll Entry is required")

	pe = frappe.get_doc("Payroll Entry", payroll_entry)

	if pe.get("__islocal"):
		frappe.throw("Save the Payroll Entry before attaching quarter charges.")

	if not pe.employees:
		frappe.throw("No employees found in Payroll Entry. Click 'Get Employees' first.")

	if not pe.start_date or not pe.end_date:
		frappe.throw("Start Date and End Date are required on Payroll Entry.")

	start = getdate(pe.start_date)
	end = getdate(pe.end_date)
	if end < start:
		frappe.throw("End Date cannot be before Start Date.")

	diff = date_diff(end, start)
	midpoint = add_days(start, diff // 2)
	payroll_date = midpoint or getdate(nowdate())

	created = []
	skipped = []

	for row in pe.employees:
		if not row.employee:
			continue

		emp = frappe.get_doc("Employee", row.employee)
		quarter = emp.get("custom_quarter")
		if not quarter:
			skipped.append({"employee": emp.name, "reason": "No quarter set"})
			continue

		q_doc = frappe.get_doc("Quarter", quarter)
		if not q_doc.charges:
			skipped.append({"employee": emp.name, "reason": "No charges in quarter"})
			continue

		for charge in q_doc.charges:
			if not charge.charge or charge.amount is None:
				continue

			exists = frappe.db.exists(
				"Additional Salary",
				{
					"ref_doctype": "Payroll Entry",
					"ref_docname": pe.name,
					"employee": emp.name,
					"salary_component": charge.charge,
					"docstatus": ["!=", 2],
				},
			)
			if exists:
				skipped.append({"employee": emp.name, "component": charge.charge, "reason": "Already exists"})
				continue

			additional = frappe.get_doc(
				{
					"doctype": "Additional Salary",
					"employee": emp.name,
					"salary_component": charge.charge,
					"amount": charge.amount,
					"company": pe.company,
					"payroll_date": payroll_date,
					"overwrite_salary_structure_amount": 1,
					"ref_doctype": "Payroll Entry",
					"ref_docname": pe.name,
				}
			)
			additional.insert(ignore_permissions=True)
			additional.submit()
			created.append(additional.name)

	frappe.db.commit()
	return {"created": created, "skipped": skipped, "payroll_date": payroll_date}

