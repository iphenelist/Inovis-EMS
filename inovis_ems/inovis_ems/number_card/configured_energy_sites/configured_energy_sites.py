import frappe

from inovis_ems.number_card_utils import get_configured_energy_sites


@frappe.whitelist()
def get():
	return get_configured_energy_sites()
