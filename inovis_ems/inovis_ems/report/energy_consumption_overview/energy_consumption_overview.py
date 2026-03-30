from frappe import _
import frappe
from frappe.utils import add_months, flt, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	filters.from_date = filters.get("from_date") or add_months(today(), -11)
	filters.to_date = filters.get("to_date") or today()

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)
	return columns, data, None, chart, summary


def get_columns():
	return [
		{
			"fieldname": "period_label",
			"label": _("Period"),
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"fieldname": "total_consumption",
			"label": _("Consumption"),
			"fieldtype": "Float",
			"width": 140,
		},
		{
			"fieldname": "total_cost",
			"label": _("Energy Cost"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "total_carbon_emission",
			"label": _("Carbon Emission (kgCO2e)"),
			"fieldtype": "Float",
			"width": 170,
		},
		{
			"fieldname": "max_peak_demand",
			"label": _("Peak Demand"),
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"fieldname": "avg_power_factor",
			"label": _("Avg Power Factor"),
			"fieldtype": "Float",
			"width": 140,
		},
	]


def get_data(filters):
	group_field = {
		"Daily": "DATE(reading_datetime)",
		"Weekly": "DATE_FORMAT(reading_datetime, '%%x-W%%v')",
		"Monthly": "DATE_FORMAT(reading_datetime, '%%Y-%%m')",
	}.get(filters.get("group_by"), "DATE_FORMAT(reading_datetime, '%%Y-%%m')")

	conditions = [
		"docstatus < 2",
		"DATE(reading_datetime) BETWEEN %(from_date)s AND %(to_date)s",
	]

	if filters.get("company"):
		conditions.append("company = %(company)s")
	if filters.get("energy_site"):
		conditions.append("energy_site = %(energy_site)s")
	if filters.get("energy_meter"):
		conditions.append("energy_meter = %(energy_meter)s")

	return frappe.db.sql(
		f"""
		SELECT
			{group_field} AS period_key,
			{group_field} AS period_label,
			SUM(consumption) AS total_consumption,
			SUM(energy_cost) AS total_cost,
			SUM(carbon_emission_kg) AS total_carbon_emission,
			MAX(peak_demand) AS max_peak_demand,
			AVG(NULLIF(power_factor, 0)) AS avg_power_factor
		FROM `tabEnergy Meter Reading`
		WHERE {' AND '.join(conditions)}
		GROUP BY period_key, period_label
		ORDER BY period_key
		""",
		filters,
		as_dict=True,
	)


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [row.period_label for row in data],
			"datasets": [
				{
					"name": _("Consumption"),
					"values": [flt(row.total_consumption) for row in data],
					"chartType": "bar",
				},
				{
					"name": _("Cost"),
					"values": [flt(row.total_cost) for row in data],
					"chartType": "line",
				},
			],
		},
		"type": "axis-mixed",
		"height": 320,
		"barOptions": {"spaceRatio": 0.2},
		"colors": ["#1b5e20", "#ff8f00"],
	}


def get_summary(data):
	if not data:
		return []

	total_consumption = sum(flt(row.total_consumption) for row in data)
	total_cost = sum(flt(row.total_cost) for row in data)
	total_carbon = sum(flt(row.total_carbon_emission) for row in data)
	max_peak = max((flt(row.max_peak_demand) for row in data), default=0)

	return [
		{
			"value": total_consumption,
			"indicator": "Green",
			"label": _("Total Consumption"),
			"datatype": "Float",
		},
		{
			"value": total_cost,
			"indicator": "Orange",
			"label": _("Total Cost"),
			"datatype": "Currency",
		},
		{
			"value": total_carbon,
			"indicator": "Blue",
			"label": _("Total Carbon Emission"),
			"datatype": "Float",
		},
		{
			"value": max_peak,
			"indicator": "Red",
			"label": _("Peak Demand"),
			"datatype": "Float",
		},
	]
