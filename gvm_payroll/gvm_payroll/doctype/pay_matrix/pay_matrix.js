// Copyright (c) 2025, Samuael Ketema and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pay Matrix", {
	refresh(frm) {
		render_matrix(frm);
	},
	pay_matrix_levels(frm) {
		render_matrix(frm);
	},
	add_level(frm) {
		create_pay_matrix_level(frm);
	},
});

async function render_matrix(frm) {
	if (!frm.doc.name) return;

	// Fetch all Pay Matrix Levels for this Pay Matrix
	const level_list = await frappe.db.get_list("Pay Matrix Level", {
		filters: { pay_matrix: frm.doc.name },
		fields: ["name"],
		order_by: "level asc",
	});

	if (!level_list.length) {
		$(frm.fields_dict.matrix_html.wrapper).html("<p>No data found.</p>");
		return;
	}

	// Fetch full doc for each level to get the child table
	const levels = [];
	for (const lvl of level_list) {
		const full_doc = await frappe.db.get_doc("Pay Matrix Level", lvl.name);
		levels.push(full_doc);
	}

	// Sort levels numerically
	// Sort levels with numeric part first, then alpha suffix (e.g., 1 < 1A < 2)
	const parseLevel = (val) => {
		const m = String(val || "").match(/^(\d+)([A-Za-z]*)$/);
		return {
			num: m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER,
			suffix: m ? m[2] || "" : "",
		};
	};
	levels.sort((a, b) => {
		const pa = parseLevel(a.level);
		const pb = parseLevel(b.level);
		if (pa.num !== pb.num) return pa.num - pb.num;
		return pa.suffix.localeCompare(pb.suffix);
	});

	// Prepare matrix data
	let all_years = new Set();
	const matrix_data = {};

	levels.forEach((lvl) => {
		matrix_data[lvl.level] = {};
		if (lvl.years && lvl.years.length) {
			lvl.years.forEach((y) => {
				matrix_data[lvl.level][y.year] = y.amount;
				all_years.add(y.year);
			});
		}
	});

	all_years = Array.from(all_years).sort((a, b) => a - b);

	// Build HTML table with styling
	let html = `
	<div class="pm-table-wrapper">
	<table class="pay-matrix-grid">
		<thead>
			<tr>
				<th class="pm-header pm-level">Level</th>`;
	levels.forEach((lvl) => {
		html += `<th data-level-name="${lvl.name}" style="border: 1px solid #ccc; padding: 4px; font-weight: bold; cursor: pointer; text-decoration: underline;">${lvl.level}</th>`;
	});
	html += `</tr>
			<tr>
				<th class="pm-header pm-year">Year</th>`;
	levels.forEach(() => {
		html += `<th class="pm-cell"></th>`; // empty cells
	});
	html += `</tr>
		</thead>
		<tbody>`;

	all_years.forEach((year) => {
		html += `<tr>
					<td class="pm-header pm-row">${year}</td>`;
		levels.forEach((lvl) => {
			let amount = matrix_data[lvl.level][year] || "";
			if (amount !== "") {
				amount = Number(amount).toLocaleString(); // add comma
			}
			html += `<td class="pm-cell">${amount}</td>`;
		});
		html += `</tr>`;
	});

	html += `</tbody></table>
	</div>
	<style>
		.pm-table-wrapper {
			width: 100%;
			overflow-x: auto;
		}
		.pay-matrix-grid {
			min-width: 960px;
			width: 100%;
			border-collapse: separate;
			border-spacing: 0;
			font-size: 0.7rem;
			text-align: center;
			border: 1px solid #d1d8dd;
			border-radius: 8px;
			overflow: hidden;
			box-shadow: 0 1px 2px rgba(0,0,0,0.05);
		}
		.pay-matrix-grid thead {
			background: #f8f9fa;
		}
		.pay-matrix-grid th,
		.pay-matrix-grid td {
			padding: 6px 8px;
			border-right: 1px solid #e1e6eb;
			border-bottom: 1px solid #e1e6eb;
		}
		.pay-matrix-grid tr:last-child td {
			border-bottom: none;
		}
		.pay-matrix-grid tr td:last-child,
		.pay-matrix-grid tr th:last-child {
			border-right: none;
		}
		.pay-matrix-grid .pm-header {
			font-weight: 600;
			background: #f8f9fa;
		}
		.pay-matrix-grid .pm-level {
			cursor: pointer;
			text-decoration: underline;
		}
		.pay-matrix-grid .pm-row {
			text-align: left;
			padding-left: 10px;
		}
		.pay-matrix-grid .pm-cell {
			font-size: 0.68rem;
		}
		.pay-matrix-grid tr:hover td {
			background: #fbfcfd;
		}
	</style>`;

	const wrapper = $(frm.fields_dict.matrix_html.wrapper);
	wrapper.html(html);
	bind_level_clicks(frm, levels);
}

function create_pay_matrix_level(frm) {
	if (!frm.doc.name) {
		frappe.msgprint(__("Please save the Pay Matrix first."));
		return;
	}

	let years_data = [];

	const d = new frappe.ui.Dialog({
		title: __("Add Pay Matrix Level"),
		fields: [
			{
				fieldname: "level",
				fieldtype: "Data",
				label: __("Level"),
				reqd: 1,
			},
			{
				fieldname: "pay_band",
				fieldtype: "Data",
				label: __("Pay Band"),
			},
			{
				fieldname: "grade",
				fieldtype: "Link",
				options: "Employee Grade",
				label: __("Grade"),
			},
			{
				fieldname: "years_html",
				fieldtype: "HTML",
				options: "",
			},
		],
		primary_action_label: __("Create"),
		primary_action: async (values) => {
			if (!values) return;
			try {
				// Get data from custom table
				const years = get_years_from_table();
				
				if (!years || years.length === 0) {
					frappe.msgprint({
						title: __("Validation Error"),
						message: __("Please add at least one year entry"),
						indicator: "orange",
					});
					return;
				}

				// Format for insert
				const years_formatted = years.map((row) => ({
					doctype: "Matrix Level Items",
					year: row.year,
					amount: row.amount,
				}));

				await frappe.call({
					method: "frappe.client.insert",
					args: {
						doc: {
							doctype: "Pay Matrix Level",
							pay_matrix: frm.doc.name,
							level: values.level,
							pay_band: values.pay_band || "",
							grade: values.grade || "",
							years: years_formatted,
						},
					},
					freeze: true,
					freeze_message: __("Creating Level..."),
				});
				d.hide();
				frappe.msgprint(__("Pay Matrix Level created"));
				render_matrix(frm);
			} catch (e) {
				console.error(e);
				frappe.msgprint({
					title: __("Error"),
					message: e.message || __("Could not create Pay Matrix Level"),
					indicator: "red",
				});
			}
		},
	});

	// Function to get years data from custom table
	function get_years_from_table() {
		const rows = d.$wrapper.find(".custom-years-table tbody tr");
		const years = [];
		rows.each(function () {
			const $row = $(this);
			const year = $row.find('input[name="year"]').val();
			const amount = parseFloat($row.find('input[name="amount"]').val());
			if (year && !isNaN(amount)) {
				years.push({ year: year, amount: amount });
			}
		});
		return years;
	}

	// Function to render custom table
	function render_custom_table() {
		const years_html = `
			<div class="custom-years-container">
				<label class="control-label">${__("Years (Year / Amount)")}</label>
				<table class="custom-years-table table table-bordered" style="margin-top: 10px;">
					<thead>
						<tr>
							<th style="width: 40%;">${__("Year")}</th>
							<th style="width: 50%;">${__("Amount")}</th>
							<th style="width: 10%;"></th>
						</tr>
					</thead>
					<tbody>
						${years_data.map((row, idx) => `
							<tr data-index="${idx}">
								<td>
									<input type="text" name="year" class="form-control" value="${row.year || ""}" placeholder="${__("Year")}" />
								</td>
								<td>
									<input type="number" name="amount" class="form-control" value="${row.amount || ""}" step="0.01" placeholder="${__("Amount")}" />
								</td>
								<td>
									<button type="button" class="btn btn-sm btn-secondary remove-row" style="width: 100%;">
										${__("Remove")}
									</button>
								</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
				<button type="button" class="btn btn-sm btn-primary add-year-row" style="margin-top: 10px;">
					${__("Add Row")}
				</button>
			</div>
			<style>
				.custom-years-container {
					margin: 15px 0;
				}
				.custom-years-table {
					font-size: 12px;
				}
				.custom-years-table input {
					font-size: 12px;
					padding: 4px 8px;
				}
				.custom-years-table th {
					background: #f8f9fa;
					font-weight: 600;
					padding: 8px;
				}
				.custom-years-table td {
					padding: 4px;
					vertical-align: middle;
				}
			</style>
		`;
		
		d.fields_dict.years_html.$wrapper.html(years_html);
		
		// Bind add row button
		d.$wrapper.find(".add-year-row").on("click", function () {
			const new_row = `
				<tr>
					<td>
						<input type="text" name="year" class="form-control" value="" placeholder="${__("Year")}" />
					</td>
					<td>
						<input type="number" name="amount" class="form-control" value="" step="0.01" placeholder="${__("Amount")}" />
					</td>
					<td>
						<button type="button" class="btn btn-sm btn-secondary remove-row" style="width: 100%;">
							${__("Remove")}
						</button>
					</td>
				</tr>
			`;
			d.$wrapper.find(".custom-years-table tbody").append(new_row);
		});
		
		// Bind remove row buttons (using event delegation)
		d.$wrapper.on("click", ".remove-row", function () {
			$(this).closest("tr").remove();
		});
	}

	// Render table after dialog is shown
	d.show();
	setTimeout(() => {
		render_custom_table();
	}, 100);
}

function bind_level_clicks(frm, levels) {
	const wrapper = $(frm.fields_dict.matrix_html.wrapper);
	wrapper.find("th[data-level-name]").on("click", async function (e) {
		e.preventDefault();
		const level_name = $(this).data("level-name");
		// Fetch fresh document with child tables
		const level_doc = await frappe.db.get_doc("Pay Matrix Level", level_name);
		if (level_doc) {
			edit_pay_matrix_level(frm, level_doc);
		}
	});
}

function edit_pay_matrix_level(frm, level_doc) {
	// Prepare initial years data
	let years_data = (level_doc.years || []).map((row) => ({
		year: row.year,
		amount: row.amount,
	}));

	const d = new frappe.ui.Dialog({
		title: __("Edit Pay Matrix Level"),
		fields: [
			{
				fieldname: "level",
				fieldtype: "Data",
				label: __("Level"),
				reqd: 1,
				default: level_doc.level,
			},
			{
				fieldname: "pay_band",
				fieldtype: "Data",
				label: __("Pay Band"),
				default: level_doc.pay_band || "",
			},
			{
				fieldname: "grade",
				fieldtype: "Link",
				options: "Employee Grade",
				label: __("Grade"),
				default: level_doc.grade || "",
			},
			{
				fieldname: "years_html",
				fieldtype: "HTML",
				options: "",
			},
		],
		primary_action_label: __("Update"),
		primary_action: async (values) => {
			if (!values) return;
			try {
				// Get data from custom table
				const years = get_years_from_table();
				
				if (!years || years.length === 0) {
					frappe.msgprint({
						title: __("Validation Error"),
						message: __("Please add at least one year entry"),
						indicator: "orange",
					});
					return;
				}

				// Call Python method to update
				const result = await frappe.call({
					method: "gvm_payroll.gvm_payroll.doctype.pay_matrix.pay_matrix.update_pay_matrix_level",
					args: {
						level_name: level_doc.name,
						level: values.level,
						pay_band: values.pay_band || "",
						grade: values.grade || "",
						years_data: years,
					},
					freeze: true,
					freeze_message: __("Updating Level..."),
				});
				
				if (result && result.message && result.message.success) {
					d.hide();
					frappe.msgprint(__("Pay Matrix Level updated"));
					render_matrix(frm);
				} else {
					throw new Error(result?.message?.message || __("Could not update Pay Matrix Level"));
				}
			} catch (e) {
				console.error(e);
				frappe.msgprint({
					title: __("Error"),
					message: e.message || __("Could not update Pay Matrix Level"),
					indicator: "red",
				});
			}
		},
	});

	// Function to get years data from custom table
	function get_years_from_table() {
		const rows = d.$wrapper.find(".custom-years-table tbody tr");
		const years = [];
		rows.each(function () {
			const $row = $(this);
			const year = $row.find('input[name="year"]').val();
			const amount = parseFloat($row.find('input[name="amount"]').val());
			if (year && !isNaN(amount)) {
				years.push({ year: year, amount: amount });
			}
		});
		return years;
	}

	// Function to render custom table
	function render_custom_table() {
		const years_html = `
			<div class="custom-years-container">
				<label class="control-label">${__("Years (Year / Amount)")}</label>
				<table class="custom-years-table table table-bordered" style="margin-top: 10px;">
					<thead>
						<tr>
							<th style="width: 40%;">${__("Year")}</th>
							<th style="width: 50%;">${__("Amount")}</th>
							<th style="width: 10%;"></th>
						</tr>
					</thead>
					<tbody>
						${years_data.map((row, idx) => `
							<tr data-index="${idx}">
								<td>
									<input type="text" name="year" class="form-control" value="${row.year || ""}" placeholder="${__("Year")}" />
								</td>
								<td>
									<input type="number" name="amount" class="form-control" value="${row.amount || ""}" step="0.01" placeholder="${__("Amount")}" />
								</td>
								<td>
									<button type="button" class="btn btn-sm btn-secondary remove-row" style="width: 100%;">
										${__("Remove")}
									</button>
								</td>
							</tr>
						`).join("")}
					</tbody>
				</table>
				<button type="button" class="btn btn-sm btn-primary add-year-row" style="margin-top: 10px;">
					${__("Add Row")}
				</button>
			</div>
			<style>
				.custom-years-container {
					margin: 15px 0;
				}
				.custom-years-table {
					font-size: 12px;
				}
				.custom-years-table input {
					font-size: 12px;
					padding: 4px 8px;
				}
				.custom-years-table th {
					background: #f8f9fa;
					font-weight: 600;
					padding: 8px;
				}
				.custom-years-table td {
					padding: 4px;
					vertical-align: middle;
				}
			</style>
		`;
		
		d.fields_dict.years_html.$wrapper.html(years_html);
		
		// Bind add row button
		d.$wrapper.find(".add-year-row").on("click", function () {
			const new_row = `
				<tr>
					<td>
						<input type="text" name="year" class="form-control" value="" placeholder="${__("Year")}" />
					</td>
					<td>
						<input type="number" name="amount" class="form-control" value="" step="0.01" placeholder="${__("Amount")}" />
					</td>
					<td>
						<button type="button" class="btn btn-sm btn-secondary remove-row" style="width: 100%;">
							${__("Remove")}
						</button>
					</td>
				</tr>
			`;
			d.$wrapper.find(".custom-years-table tbody").append(new_row);
		});
		
		// Bind remove row buttons (using event delegation)
		d.$wrapper.on("click", ".remove-row", function () {
			$(this).closest("tr").remove();
		});
	}

	// Render table after dialog is shown
	d.show();
	setTimeout(() => {
		render_custom_table();
	}, 100);

	d.set_secondary_action_label(__("Delete"));
	d.set_secondary_action(async () => {
		frappe.confirm(
			__("Delete this Pay Matrix Level and its rows?"),
			async () => {
				try {
					await frappe.call({
						method: "frappe.client.delete",
						args: {
							doctype: "Pay Matrix Level",
							name: level_doc.name,
						},
						freeze: true,
						freeze_message: __("Deleting Level..."),
					});
					d.hide();
					frappe.msgprint(__("Pay Matrix Level deleted"));
					render_matrix(frm);
				} catch (e) {
					console.error(e);
					frappe.msgprint({
						title: __("Error"),
						message: e.message || __("Could not delete Pay Matrix Level"),
						indicator: "red",
					});
				}
			}
		);
	});

	d.show();
}
