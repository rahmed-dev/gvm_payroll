frappe.query_reports["Bank Cover Letter"] = {
	onload: function(report) {
		// Function to generate period labels from dates
		function generate_period_labels() {
			const from_date = frappe.query_report.get_filter_value("from_date");
			const to_date = frappe.query_report.get_filter_value("to_date");

			if (from_date && to_date) {
				const from_moment = frappe.datetime.str_to_obj(from_date);
				const to_moment = frappe.datetime.str_to_obj(to_date);

				// Get short month names (Jan, Feb, etc.)
				const month_names_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
				const from_month = month_names_short[from_moment.getMonth()];
				const from_year = String(from_moment.getFullYear()).slice(-2); // Last 2 digits
				const to_month = month_names_short[to_moment.getMonth()];
				const to_year = String(to_moment.getFullYear()).slice(-2); // Last 2 digits

				// Both use from_date only
				let month_label = from_month + "-" + from_year;
				let period_title = from_month + "-" + from_year;

				frappe.query_report.set_filter_value("month_label", month_label);
				frappe.query_report.set_filter_value("period_title", period_title);
			}
		}

		// Function to load company defaults
		function load_company_defaults() {
			const company = frappe.query_report.get_filter_value("company");
			if (company) {
				frappe.db.get_value("Company", company, [
					"custom_company_address",
					"custom_bank_name",
					"custom_bank_address"
				]).then(r => {
					if (r.message) {
						frappe.query_report.set_filter_value("company_address", r.message.custom_company_address || "");
						frappe.query_report.set_filter_value("bank_name", r.message.custom_bank_name || "");
						frappe.query_report.set_filter_value("bank_address", r.message.custom_bank_address || "");
					}
				});
			}

			// Also generate period labels
			generate_period_labels();
		}

		// Attach event to company filter
		report.page.fields_dict.company.$input.on('change', function() {
			load_company_defaults();
		});

		// Manual button as backup
		report.page.add_inner_button(__("Load Company Defaults"), function() {
			load_company_defaults();
			frappe.show_alert({message: __("Defaults loaded"), indicator: "green"});
		});
	},
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "company_address",
			label: __("Company Address"),
			fieldtype: "Data",
		},
		{
			fieldname: "bank_name",
			label: __("Bank Name"),
			fieldtype: "Data",
		},
		{
			fieldname: "bank_address",
			label: __("Bank Address"),
			fieldtype: "Data",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "period_title",
			label: __("Period Title"),
			fieldtype: "Data",
			default: __("Salary for the selected period"),
		},
		{
			fieldname: "month_label",
			label: __("Month Label"),
			fieldtype: "Data",
		},
		{
			fieldname: "cheque_no",
			label: __("Cheque No."),
			fieldtype: "Data",
		},
		{
			fieldname: "cheque_date",
			label: __("Cheque Date"),
			fieldtype: "Date",
		},
	],
};

