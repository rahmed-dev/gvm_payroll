// Copyright (c) 2025, Samuael Ketema and contributors
// For license information, please see license.txt

frappe.ui.form.on("Bulk Additional Salary", {
	refresh(frm) {
		// Remove all custom buttons first and clear flags
		frm.page.clear_actions();
		frm.page.btn_create_additional_salaries = null;
		frm.page.btn_submit_additional_salaries = null;

		// Before saving: NO button visible - return immediately
		if (frm.doc.__islocal) {
			return;
		}

		// After saving: check if additional salaries exist
		check_and_show_buttons(frm);
	},

	// When default quarter changes, populate existing empty rows
	default_quarter: function(frm) {
		if (frm.doc.default_quarter && frm.doc.charges) {
			frm.doc.charges.forEach(function(row) {
				// Only populate if row's quarter is empty
				if (!row.quarter) {
					frappe.model.set_value(row.doctype, row.name, 'quarter', frm.doc.default_quarter);
				}
			});
		}
		frm.refresh_field('charges');
	},

	// When default salary component changes, populate existing empty rows
	default_salary_component: function(frm) {
		if (frm.doc.default_salary_component && frm.doc.charges) {
			frm.doc.charges.forEach(function(row) {
				// Only populate if row's salary component is empty
				if (!row.salary_component) {
					frappe.model.set_value(row.doctype, row.name, 'salary_component', frm.doc.default_salary_component);
				}
			});
		}
		frm.refresh_field('charges');
	}
});

// Auto-populate default values when new row is added to charges table
frappe.ui.form.on("Bulk Additional Salary Item", {
	charges_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];

		// Only populate if fields are empty (new row)
		// This ensures we don't overwrite existing data
		if (!row.quarter && frm.doc.default_quarter) {
			frappe.model.set_value(cdt, cdn, 'quarter', frm.doc.default_quarter);
		}

		if (!row.salary_component && frm.doc.default_salary_component) {
			frappe.model.set_value(cdt, cdn, 'salary_component', frm.doc.default_salary_component);
		}
	}
});

async function check_and_show_buttons(frm) {
	// Check if additional salaries have been created for this document
	const additional_salaries = await frappe.db.get_list("Additional Salary", {
		filters: {
			ref_doctype: "Bulk Additional Salary",
			ref_docname: frm.doc.name,
		},
		fields: ["name", "docstatus"],
		limit: 1,
	});

	if (additional_salaries && additional_salaries.length > 0) {
		// Additional salaries exist - check if any are not submitted
		const not_submitted = await frappe.db.get_list("Additional Salary", {
			filters: {
				ref_doctype: "Bulk Additional Salary",
				ref_docname: frm.doc.name,
				docstatus: 0, // Draft (not submitted)
			},
			limit: 1,
		});

		if (not_submitted.length === 0) {
			// All additional salaries are submitted
			// Submit the Bulk Additional Salary document if not already submitted
			if (frm.doc.docstatus === 0) {
				try {
					await frm.save();
					await frm.submit();
					frappe.msgprint(__("Bulk Additional Salary submitted"));
					frm.reload_doc();
				} catch (e) {
					console.error(e);
					frappe.msgprint({
						title: __("Error"),
						message: e.message || __("Could not submit Bulk Additional Salary"),
						indicator: "red",
					});
				}
			}
			// No buttons shown after submission
		} else {
			// Show "Submit Additional Salaries" button (only one)
			if (!frm.page.btn_submit_additional_salaries) {
				const btn = frm.page.add_button(__("Submit Additional Salaries"), () =>
					submit_additional_salaries(frm)
				);
				if (btn) {
					$(btn).removeClass("btn-default btn-secondary btn-primary").addClass("btn-dark");
					frm.page.btn_submit_additional_salaries = btn;
				}
			}
		}
	} else {
		// No additional salaries created yet - show "Create Additional Salaries" button (only one)
		if (!frm.page.btn_create_additional_salaries) {
			const btn = frm.page.add_button(__("Create Additional Salaries"), () =>
				create_bulk_additional_salary(frm)
			);
			if (btn) {
				$(btn).removeClass("btn-default btn-secondary btn-primary").addClass("btn-dark");
				frm.page.btn_create_additional_salaries = btn;
			}
		}
	}
}

async function create_bulk_additional_salary(frm) {
	if (!frm.doc.company || !frm.doc.payroll_date) {
		frappe.msgprint({
			title: __("Missing Data"),
			message: __("Please set Company and Payroll Date before processing."),
			indicator: "orange",
		});
		return;
	}

	if (!frm.doc.charges || !frm.doc.charges.length) {
		frappe.msgprint({
			title: __("Missing Data"),
			message: __("Add at least one charge row to process."),
			indicator: "orange",
		});
		return;
	}

	try {
		await frappe.call({
			method: "gvm_payroll.gvm_payroll.doctype.bulk_additional_salary.bulk_additional_salary.create_additional_salaries",
			args: {
				docname: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Creating Additional Salaries..."),
		});
		frappe.msgprint(__("Additional Salary records created"));
		frm.reload_doc();
	} catch (e) {
		console.error(e);
		frappe.msgprint({
			title: __("Error"),
			message: e.message || __("Could not create Additional Salaries"),
			indicator: "red",
		});
	}
}

async function submit_additional_salaries(frm) {
	try {
		await frappe.call({
			method: "gvm_payroll.gvm_payroll.doctype.bulk_additional_salary.bulk_additional_salary.submit_additional_salaries",
			args: {
				docname: frm.doc.name,
			},
			freeze: true,
			freeze_message: __("Submitting Additional Salaries..."),
		});
		frappe.msgprint(__("All Additional Salary records submitted"));
		frm.reload_doc();
	} catch (e) {
		console.error(e);
		frappe.msgprint({
			title: __("Error"),
			message: e.message || __("Could not submit Additional Salaries"),
			indicator: "red",
		});
	}
}
