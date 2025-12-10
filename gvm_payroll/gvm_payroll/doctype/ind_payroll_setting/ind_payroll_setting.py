# Copyright (c) 2025, Samuael Ketema and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class INDPayrollSetting(Document):
	pass


@frappe.whitelist()
def get_increment_dates(doctype, txt, searchfield, start, page_len, filters):
	"""Get increment dates for date field filter"""
	increment_dates = []
	company = filters.get("company") if filters else None
	
	# Get increment dates from IND Payroll Setting
	if company:
		setting = frappe.db.get_value("IND Payroll Setting", {"company": company}, "name")
		if setting:
			setting_doc = frappe.get_doc("IND Payroll Setting", setting)
			for inc_date in setting_doc.increment_dates:
				if inc_date.increment_date:
					increment_dates.append([inc_date.increment_date])
	
	# If no company-specific dates, get from any setting
	if not increment_dates:
		payroll_settings = frappe.get_all("IND Payroll Setting", fields=["name"], limit=1)
		if payroll_settings:
			setting_doc = frappe.get_doc("IND Payroll Setting", payroll_settings[0].name)
			for inc_date in setting_doc.increment_dates:
				if inc_date.increment_date:
					increment_dates.append([inc_date.increment_date])
	
	# If still no dates, return empty (will allow any date)
	return increment_dates


@frappe.whitelist()
def get_increment_dates_list(company=None):
	"""Get list of increment dates as actual date strings for current year"""
	from frappe.utils import getdate, nowdate
	
	def get_increment_date_from_string(date_str, year):
		if date_str == "1st April":
			return getdate(f"{year}-04-01")
		elif date_str == "1st October":
			return getdate(f"{year}-10-01")
		return None
	
	increment_date_strings = []
	current_year = getdate(nowdate()).year
	
	# Get increment date strings from IND Payroll Setting
	if company:
		setting = frappe.db.get_value("IND Payroll Setting", {"company": company}, "name")
		if setting:
			setting_doc = frappe.get_doc("IND Payroll Setting", setting)
			for inc_date in setting_doc.increment_dates:
				if inc_date.increment_date and inc_date.increment_date not in increment_date_strings:
					increment_date_strings.append(inc_date.increment_date)
	
	# If no company-specific dates, get from any setting
	if not increment_date_strings:
		payroll_settings = frappe.get_all("IND Payroll Setting", fields=["name"], limit=1)
		if payroll_settings:
			setting_doc = frappe.get_doc("IND Payroll Setting", payroll_settings[0].name)
			for inc_date in setting_doc.increment_dates:
				if inc_date.increment_date and inc_date.increment_date not in increment_date_strings:
					increment_date_strings.append(inc_date.increment_date)
	
	# If still no dates, use defaults
	if not increment_date_strings:
		increment_date_strings = ["1st April", "1st October"]
	
	# Convert to actual dates for current year
	increment_dates = []
	for date_str in increment_date_strings:
		date_obj = get_increment_date_from_string(date_str, current_year)
		if date_obj:
			increment_dates.append(str(date_obj))
	
	return increment_dates

