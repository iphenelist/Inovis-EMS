import frappe
from frappe.model.document import Document
from frappe.utils import random_string


class EnergyDataSource(Document):
	def before_insert(self):
		if not self.authentication_token:
			self.authentication_token = random_string(32)

	def validate(self):
		if self.default_meter and not self.default_energy_site:
			self.default_energy_site = frappe.db.get_value(
				"Energy Meter", self.default_meter, "energy_site"
			)
