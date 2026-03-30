import frappe

from inovis_ems.number_card_utils import get_active_energy_meters


@frappe.whitelist()
def get():
	return get_active_energy_meters()
