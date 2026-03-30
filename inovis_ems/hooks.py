app_name = "inovis_ems"
app_title = "Inovis EMS"
app_publisher = "Innocent Phenelist Metumba"
app_description = "Energy Management System (EMS)"
app_email = "innocentphenelist@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "inovis_ems",
# 		"logo": "/assets/inovis_ems/logo.png",
# 		"title": "Inovis EMS",
# 		"route": "/inovis_ems",
# 		"has_permission": "inovis_ems.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/inovis_ems/css/inovis_ems.css"
# app_include_js = "/assets/inovis_ems/js/inovis_ems.js"

# include js, css files in header of web template
# web_include_css = "/assets/inovis_ems/css/inovis_ems.css"
# web_include_js = "/assets/inovis_ems/js/inovis_ems.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "inovis_ems/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Purchase Invoice": "public/js/purchase_invoice.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "inovis_ems/public/icons.svg"

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
# 	"methods": "inovis_ems.utils.jinja_methods",
# 	"filters": "inovis_ems.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "inovis_ems.install.before_install"
after_install = "inovis_ems.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "inovis_ems.uninstall.before_uninstall"
# after_uninstall = "inovis_ems.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "inovis_ems.utils.before_app_install"
# after_app_install = "inovis_ems.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "inovis_ems.utils.before_app_uninstall"
# after_app_uninstall = "inovis_ems.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "inovis_ems.notifications.get_notification_config"

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
	"Energy Meter Reading": {
		"on_update": [
			"inovis_ems.erpnext_integration.sync_purchase_invoice_energy_fields",
			"inovis_ems.alerts.evaluate_reading_alerts",
		],
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"inovis_ems.alerts.evaluate_recent_readings",
	]
}

after_migrate = "inovis_ems.install.after_install"

# Testing
# -------

# before_tests = "inovis_ems.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "inovis_ems.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "inovis_ems.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["inovis_ems.utils.before_request"]
# after_request = ["inovis_ems.utils.after_request"]

# Job Events
# ----------
# before_job = ["inovis_ems.utils.before_job"]
# after_job = ["inovis_ems.utils.after_job"]

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
# 	"inovis_ems.auth.validate"
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
