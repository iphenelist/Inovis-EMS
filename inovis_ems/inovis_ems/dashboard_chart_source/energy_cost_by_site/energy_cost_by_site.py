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
	from_date = from_date or filters.get("from_date") or add_months(today(), -2)
	to_date = to_date or filters.get("to_date") or today()

	conditions = [
		"docstatus < 2",
		"DATE(reading_datetime) BETWEEN %(from_date)s AND %(to_date)s",
	]
	values = {"from_date": from_date, "to_date": to_date}

	if filters.get("company"):
		conditions.append("company = %(company)s")
		values["company"] = filters.company

	data = frappe.db.sql(
		f"""
		SELECT
			energy_site AS label,
			SUM(energy_cost) AS value
		FROM `tabEnergy Meter Reading`
		WHERE {' AND '.join(conditions)} AND IFNULL(energy_site, '') != ''
		GROUP BY energy_site
		ORDER BY value DESC
		LIMIT 10
		""",
		values,
		as_dict=True,
	)

	return {
		"labels": [row.label for row in data],
		"datasets": [{"name": _("Energy Cost"), "values": [row.value for row in data]}],
		"type": "bar",
	}
