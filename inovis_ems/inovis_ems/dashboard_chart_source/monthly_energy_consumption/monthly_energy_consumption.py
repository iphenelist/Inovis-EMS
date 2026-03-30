import frappe
from frappe import _
from frappe.utils import add_months, today
from frappe.utils.dashboard import cache_source


@frappe.whitelist()
@cache_source
def get(
	chart_name=None,
	chart=None,
	no_cache=None,
	filters=None,
	from_date=None,
	to_date=None,
	timespan=None,
	time_interval=None,
	heatmap_year=None,
):
	filters = frappe._dict(frappe.parse_json(filters) or {})
	from_date = from_date or filters.get("from_date") or add_months(today(), -11)
	to_date = to_date or filters.get("to_date") or today()

	conditions = [
		"docstatus < 2",
		"DATE(reading_datetime) BETWEEN %(from_date)s AND %(to_date)s",
	]
	values = {"from_date": from_date, "to_date": to_date}

	if filters.get("company"):
		conditions.append("company = %(company)s")
		values["company"] = filters.company
	if filters.get("energy_site"):
		conditions.append("energy_site = %(energy_site)s")
		values["energy_site"] = filters.energy_site
	if filters.get("energy_meter"):
		conditions.append("energy_meter = %(energy_meter)s")
		values["energy_meter"] = filters.energy_meter

	data = frappe.db.sql(
		f"""
		SELECT
			DATE_FORMAT(reading_datetime, '%%Y-%%m') AS label,
			SUM(consumption) AS value
		FROM `tabEnergy Meter Reading`
		WHERE {' AND '.join(conditions)}
		GROUP BY DATE_FORMAT(reading_datetime, '%%Y-%%m')
		ORDER BY DATE_FORMAT(reading_datetime, '%%Y-%%m')
		""",
		values,
		as_dict=True,
	)

	return {
		"labels": [row.label for row in data],
		"datasets": [{"name": _("Consumption"), "values": [row.value for row in data]}],
		"type": "line",
	}
