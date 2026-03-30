import frappe
from frappe import _
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
			"fieldname": "purchase_invoice",
			"label": _("Purchase Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 180,
		},
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"fieldname": "company",
			"label": _("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"width": 180,
		},
		{
			"fieldname": "supplier",
			"label": _("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 180,
		},
		{
			"fieldname": "energy_site",
			"label": _("Energy Site"),
			"fieldtype": "Link",
			"options": "Energy Site",
			"width": 180,
		},
		{
			"fieldname": "energy_meter",
			"label": _("Energy Meter"),
			"fieldtype": "Link",
			"options": "Energy Meter",
			"width": 180,
		},
		{
			"fieldname": "base_grand_total",
			"label": _("Base Grand Total"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "outstanding_amount",
			"label": _("Outstanding"),
			"fieldtype": "Currency",
			"width": 140,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120,
		},
	]


def get_data(filters):
	conditions = [
		"docstatus < 2",
		"posting_date BETWEEN %(from_date)s AND %(to_date)s",
		"IFNULL(is_energy_invoice, 0) = 1",
	]

	if filters.get("company"):
		conditions.append("company = %(company)s")
	if filters.get("energy_site"):
		conditions.append("energy_site = %(energy_site)s")
	if filters.get("status"):
		conditions.append("status = %(status)s")

	return frappe.db.sql(
		f"""
		SELECT
			name AS purchase_invoice,
			posting_date,
			company,
			supplier,
			energy_site,
			energy_meter,
			base_grand_total,
			outstanding_amount,
			status
		FROM `tabPurchase Invoice`
		WHERE {' AND '.join(conditions)}
		ORDER BY posting_date DESC, modified DESC
		""",
		filters,
		as_dict=True,
	)


def get_chart(data):
	if not data:
		return None

	monthly = {}
	for row in data:
		period = row.posting_date.strftime("%Y-%m")
		monthly.setdefault(period, 0)
		monthly[period] += flt(row.base_grand_total)

	return {
		"data": {
			"labels": list(monthly.keys()),
			"datasets": [
				{
					"name": _("Energy Spend"),
					"values": [flt(value) for value in monthly.values()],
				}
			],
		},
		"type": "bar",
		"height": 300,
		"colors": ["#0f766e"],
	}


def get_summary(data):
	if not data:
		return []

	total_amount = sum(flt(row.base_grand_total) for row in data)
	total_outstanding = sum(flt(row.outstanding_amount) for row in data)

	return [
		{
			"value": len(data),
			"indicator": "Blue",
			"label": _("Energy Purchase Invoices"),
			"datatype": "Int",
		},
		{
			"value": total_amount,
			"indicator": "Green",
			"label": _("Total Spend"),
			"datatype": "Currency",
		},
		{
			"value": total_outstanding,
			"indicator": "Orange",
			"label": _("Outstanding Amount"),
			"datatype": "Currency",
		},
	]
