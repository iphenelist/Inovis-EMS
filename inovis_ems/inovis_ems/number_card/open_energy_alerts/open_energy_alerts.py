import frappe

from inovis_ems.number_card_utils import get_open_energy_alerts


@frappe.whitelist()
def get():
	return get_open_energy_alerts()
