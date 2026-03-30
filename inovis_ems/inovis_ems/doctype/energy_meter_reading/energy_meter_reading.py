import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class EnergyMeterReading(Document):
	def validate(self):
		self.sync_context()
		self.set_opening_reading()
		self.calculate_metrics()
		self.validate_readings()

	def sync_context(self):
		if not self.energy_meter:
			return

		meter = frappe.db.get_value(
			"Energy Meter",
			self.energy_meter,
			[
				"company",
				"energy_site",
				"unit",
				"default_rate",
				"multiplier",
			],
			as_dict=True,
		)

		if not meter:
			return

		self.company = self.company or meter.company
		self.energy_site = self.energy_site or meter.energy_site
		self.unit = self.unit or meter.unit
		self.rate = flt(self.rate) or flt(meter.default_rate)
		self.multiplier = flt(self.multiplier) or flt(meter.multiplier) or 1

		if self.energy_site and not self.project:
			self.project = frappe.db.get_value("Energy Site", self.energy_site, "project")

		if not flt(self.carbon_emission_factor):
			self.carbon_emission_factor = flt(
				frappe.db.get_single_value("Energy Settings", "carbon_emission_factor") or 0
			)

	def set_opening_reading(self):
		if self.opening_reading not in (None, "") or not (self.energy_meter and self.reading_datetime):
			return

		previous = frappe.get_all(
			"Energy Meter Reading",
			filters={
				"energy_meter": self.energy_meter,
				"docstatus": ["<", 2],
				"reading_datetime": ["<", self.reading_datetime],
				"name": ["!=", self.name],
			},
			fields=["closing_reading"],
			order_by="reading_datetime desc",
			limit=1,
		)

		if previous:
			self.opening_reading = previous[0].closing_reading

	def calculate_metrics(self):
		delta = flt(self.closing_reading) - flt(self.opening_reading)
		multiplier = flt(self.multiplier) or 1

		self.consumption = delta * multiplier
		self.energy_cost = flt(self.consumption) * flt(self.rate)
		self.carbon_emission_kg = flt(self.consumption) * flt(self.carbon_emission_factor)

	def validate_readings(self):
		if flt(self.closing_reading) < flt(self.opening_reading):
			frappe.throw(_("Closing Reading cannot be less than Opening Reading."))

		if flt(self.consumption) < 0:
			frappe.throw(_("Consumption cannot be negative."))
