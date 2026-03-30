import frappe
from frappe.utils import getdate


EMS_PI_FIELDS = {
	"is_energy_invoice",
	"energy_site",
	"energy_meter",
	"energy_data_source",
	"energy_service_period_from",
	"energy_service_period_to",
}


def sync_purchase_invoice_energy_fields(doc, method=None):
	if not getattr(doc, "purchase_invoice", None):
		return

	if not purchase_invoice_has_ems_fields():
		return

	posting_date = getdate(doc.reading_datetime) if getattr(doc, "reading_datetime", None) else None
	pi_values = frappe.db.get_value(
		"Purchase Invoice",
		doc.purchase_invoice,
		["energy_service_period_from", "energy_service_period_to"],
		as_dict=True,
	)

	if not pi_values:
		return

	service_from = min_date(pi_values.energy_service_period_from, posting_date)
	service_to = max_date(pi_values.energy_service_period_to, posting_date)

	values_to_update = {
		"is_energy_invoice": 1,
		"energy_site": doc.energy_site,
		"energy_meter": doc.energy_meter,
		"energy_data_source": doc.ingestion_source,
		"energy_service_period_from": service_from,
		"energy_service_period_to": service_to,
	}

	for fieldname, value in values_to_update.items():
		frappe.db.set_value(
			"Purchase Invoice",
			doc.purchase_invoice,
			fieldname,
			value,
			update_modified=False,
		)


def purchase_invoice_has_ems_fields():
	meta = frappe.get_meta("Purchase Invoice")
	return all(meta.has_field(fieldname) for fieldname in EMS_PI_FIELDS)


def min_date(existing, candidate):
	existing = getdate(existing) if existing else None
	candidate = getdate(candidate) if candidate else None
	if not existing:
		return candidate
	if not candidate:
		return existing
	return min(existing, candidate)


def max_date(existing, candidate):
	existing = getdate(existing) if existing else None
	candidate = getdate(candidate) if candidate else None
	if not existing:
		return candidate
	if not candidate:
		return existing
	return max(existing, candidate)
