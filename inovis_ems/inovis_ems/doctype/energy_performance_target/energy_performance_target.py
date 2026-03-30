import frappe
from frappe import _
from frappe.model.document import Document


class EnergyPerformanceTarget(Document):
	def validate(self):
		self.validate_date_ranges()

	def validate_date_ranges(self):
		if self.baseline_from and self.baseline_to and self.baseline_from > self.baseline_to:
			frappe.throw(_("Baseline From cannot be after Baseline To."))

		if self.target_from and self.target_to and self.target_from > self.target_to:
			frappe.throw(_("Target From cannot be after Target To."))
