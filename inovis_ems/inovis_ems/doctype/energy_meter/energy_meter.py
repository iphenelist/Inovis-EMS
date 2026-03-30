import frappe
from frappe.model.document import Document


class EnergyMeter(Document):
	def validate(self):
		if self.energy_site and not self.company:
			self.company = frappe.db.get_value("Energy Site", self.energy_site, "company")
