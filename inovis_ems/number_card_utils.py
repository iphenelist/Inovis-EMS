import frappe
from frappe.utils import flt, get_first_day, get_last_day, today


def get_configured_energy_sites():
	return {
		"value": frappe.db.count("Energy Site", {"docstatus": ["<", 2]}),
		"fieldtype": "Int",
		"route": ["List", "Energy Site", "List"],
	}


def get_active_energy_meters():
	return {
		"value": frappe.db.count("Energy Meter", {"docstatus": ["<", 2], "is_active": 1}),
		"fieldtype": "Int",
		"route": ["List", "Energy Meter", "List"],
		"route_options": {"is_active": 1},
	}


def get_readings_this_month():
	from_date, to_date = get_month_dates()
	return {
		"value": frappe.db.count(
			"Energy Meter Reading",
			{
				"docstatus": ["<", 2],
				"reading_datetime": ["between", [from_date, f"{to_date} 23:59:59"]],
			},
		),
		"fieldtype": "Int",
		"route": ["List", "Energy Meter Reading", "List"],
		"route_options": {"reading_datetime": ["between", [from_date, f"{to_date} 23:59:59"]]},
	}


def get_energy_cost_this_month():
	from_date, to_date = get_month_dates()
	value = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(energy_cost), 0)
		FROM `tabEnergy Meter Reading`
		WHERE docstatus < 2
			AND reading_datetime BETWEEN %s AND %s
		""",
		(from_date, f"{to_date} 23:59:59"),
	)[0][0]
	return {
		"value": flt(value),
		"fieldtype": "Currency",
		"route": ["query-report", "Energy Consumption Overview"],
		"route_options": {"from_date": from_date, "to_date": to_date},
	}


def get_open_energy_alerts():
	return {
		"value": frappe.db.count(
			"Energy Alert",
			{"docstatus": ["<", 2], "status": ["in", ["Open", "Acknowledged"]]},
		),
		"fieldtype": "Int",
		"route": ["List", "Energy Alert", "List"],
		"route_options": {"status": ["in", ["Open", "Acknowledged"]]},
	}


def get_active_performance_targets():
	return {
		"value": frappe.db.count(
			"Energy Performance Target",
			{"docstatus": ["<", 2], "is_active": 1},
		),
		"fieldtype": "Int",
		"route": ["List", "Energy Performance Target", "List"],
		"route_options": {"is_active": 1},
	}


def get_month_dates():
	current = today()
	return get_first_day(current), get_last_day(current)
