import frappe
from frappe.utils import add_to_date, flt, now_datetime


METRIC_FIELD_MAP = {
	"Consumption": "consumption",
	"Cost": "energy_cost",
	"Peak Demand": "peak_demand",
	"Carbon Emission": "carbon_emission_kg",
	"Power Factor": "power_factor",
}


def evaluate_reading_alerts(doc, method=None):
	if not doc.energy_meter:
		return

	for rule in get_matching_rules(doc):
		result = evaluate_rule(rule, doc)
		if result["matched"]:
			create_or_update_alert(rule, doc, result)
		else:
			close_open_alerts(rule, doc.energy_meter)


def evaluate_recent_readings():
	readings = frappe.get_all(
		"Energy Meter Reading",
		filters={
			"docstatus": ["<", 2],
			"modified": [">=", add_to_date(now_datetime(), hours=-24)],
		},
		pluck="name",
	)

	for reading_name in readings:
		evaluate_reading_alerts(frappe.get_doc("Energy Meter Reading", reading_name))


def get_matching_rules(doc):
	rules = frappe.get_all(
		"Energy Alert Rule",
		filters={"is_enabled": 1},
		fields=["name"],
		order_by="modified desc",
	)
	matching = []
	for row in rules:
		rule = frappe.get_doc("Energy Alert Rule", row.name)
		if rule.company and rule.company != doc.company:
			continue
		if rule.energy_site and rule.energy_site != doc.energy_site:
			continue
		if rule.energy_meter and rule.energy_meter != doc.energy_meter:
			continue
		matching.append(rule)
	return matching


def evaluate_rule(rule, doc):
	fieldname = METRIC_FIELD_MAP.get(rule.metric)
	current_value = flt(getattr(doc, fieldname, 0))

	if rule.rule_type == "Percentage Variance":
		variance_percent = get_variance_percent(doc, fieldname, rule.lookback_readings)
		if variance_percent is None:
			return {"matched": False}
		matched = compare(rule.comparison, variance_percent, rule.threshold_value)
		return {
			"matched": matched,
			"metric_value": current_value,
			"threshold_value": flt(rule.threshold_value),
			"variance_percent": variance_percent,
			"description": (
				f"{rule.metric} variance is {variance_percent:.2f}% against a trailing "
				f"average of the last {rule.lookback_readings} reading(s)."
			),
		}

	matched = compare(rule.comparison, current_value, rule.threshold_value)
	return {
		"matched": matched,
		"metric_value": current_value,
		"threshold_value": flt(rule.threshold_value),
		"variance_percent": None,
		"description": f"{rule.metric} is {current_value:.2f} and breached the configured threshold.",
	}


def get_variance_percent(doc, fieldname, lookback_readings):
	rows = frappe.get_all(
		"Energy Meter Reading",
		filters={
			"energy_meter": doc.energy_meter,
			"docstatus": ["<", 2],
			"reading_datetime": ["<", doc.reading_datetime],
			"name": ["!=", doc.name],
		},
		fields=[fieldname],
		order_by="reading_datetime desc",
		limit=lookback_readings or 3,
	)
	values = [flt(row.get(fieldname)) for row in rows if flt(row.get(fieldname))]
	if not values:
		return None

	average = sum(values) / len(values)
	if not average:
		return None

	current_value = flt(getattr(doc, fieldname, 0))
	return ((current_value - average) / average) * 100


def compare(comparison, left_value, right_value):
	if comparison == "Below":
		return flt(left_value) < flt(right_value)
	return flt(left_value) > flt(right_value)


def create_or_update_alert(rule, doc, result):
	existing_name = frappe.db.get_value(
		"Energy Alert",
		{
			"energy_alert_rule": rule.name,
			"energy_meter_reading": doc.name,
		},
	)
	alert = frappe.get_doc("Energy Alert", existing_name) if existing_name else frappe.new_doc("Energy Alert")

	alert.alert_title = f"{rule.metric} alert for {doc.energy_meter}"
	alert.company = doc.company
	alert.energy_site = doc.energy_site
	alert.energy_meter = doc.energy_meter
	alert.energy_alert_rule = rule.name
	alert.energy_meter_reading = doc.name
	alert.event_datetime = doc.reading_datetime or now_datetime()
	alert.metric = rule.metric
	alert.metric_value = result.get("metric_value")
	alert.threshold_value = result.get("threshold_value")
	alert.variance_percent = result.get("variance_percent")
	alert.status = "Open"
	alert.severity = rule.severity
	alert.description = result.get("description")

	if existing_name:
		alert.save(ignore_permissions=True)
	else:
		alert.insert(ignore_permissions=True)


def close_open_alerts(rule, energy_meter):
	alert_names = frappe.get_all(
		"Energy Alert",
		filters={
			"energy_alert_rule": rule.name,
			"energy_meter": energy_meter,
			"status": ["in", ["Open", "Acknowledged"]],
		},
		pluck="name",
	)

	for alert_name in alert_names:
		alert = frappe.get_doc("Energy Alert", alert_name)
		alert.status = "Closed"
		alert.resolved_on = now_datetime()
		alert.save(ignore_permissions=True)
