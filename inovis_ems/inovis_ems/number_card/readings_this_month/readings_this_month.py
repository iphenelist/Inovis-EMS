import frappe

from inovis_ems.number_card_utils import get_readings_this_month


@frappe.whitelist()
def get():
	return get_readings_this_month()
