app_name = "jvm_payroll"
app_title = "JVM Payroll"
app_publisher = "Samuael Ketema"
app_description = "A Payroll App for indian JVM payroll with pay matrix."
app_email = "lijsamuael@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "gvm_payroll",
# 		"logo": "/assets/gvm_payroll/logo.png",
# 		"title": "Gvm Payroll",
# 		"route": "/gvm_payroll",
# 		"has_permission": "gvm_payroll.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/gvm_payroll/css/gvm_payroll.css"
# app_include_js = "/assets/gvm_payroll/js/gvm_payroll.js"

# include js, css files in header of web template
# web_include_css = "/assets/gvm_payroll/css/gvm_payroll.css"
# web_include_js = "/assets/gvm_payroll/js/gvm_payroll.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "gvm_payroll/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "gvm_payroll/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "gvm_payroll.utils.jinja_methods",
# 	"filters": "gvm_payroll.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "gvm_payroll.install.before_install"
# after_install = "gvm_payroll.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "gvm_payroll.uninstall.before_uninstall"
# after_uninstall = "gvm_payroll.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "gvm_payroll.utils.before_app_install"
# after_app_install = "gvm_payroll.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "gvm_payroll.utils.before_app_uninstall"
# after_app_uninstall = "gvm_payroll.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "gvm_payroll.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Salary Slip": {
		"before_save": "gvm_payroll.gvm_payroll.overrides.salary_slip.split_internal_components",
		"before_submit": "gvm_payroll.gvm_payroll.overrides.salary_slip.split_internal_components"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"gvm_payroll.tasks.all"
# 	],
# 	"daily": [
# 		"gvm_payroll.tasks.daily"
# 	],
# 	"hourly": [
# 		"gvm_payroll.tasks.hourly"
# 	],
# 	"weekly": [
# 		"gvm_payroll.tasks.weekly"
# 	],
# 	"monthly": [
# 		"gvm_payroll.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "gvm_payroll.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "gvm_payroll.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "gvm_payroll.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["gvm_payroll.utils.before_request"]
# after_request = ["gvm_payroll.utils.after_request"]

# Job Events
# ----------
# before_job = ["gvm_payroll.utils.before_job"]
# after_job = ["gvm_payroll.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"gvm_payroll.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
    {
        "dt": "Custom Field",
    },
    {
        "dt": "Client Script",
    },
    {
        "dt": "Server Script",
    },
    {
        "dt": "Property Setter",
    }
]