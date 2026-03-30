import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def ingest_meter_readings(source_name=None, token=None, readings=None):
	source_name = source_name or frappe.form_dict.get("source_name")
	token = token or frappe.form_dict.get("token")
	readings = readings or frappe.form_dict.get("readings")

	if not source_name or not token:
		frappe.throw(_("source_name and token are required."))

	source = frappe.get_doc("Energy Data Source", source_name)
	if not source.is_enabled:
		frappe.throw(_("Energy Data Source is disabled."))

	if source.authentication_token != token:
		frappe.throw(_("Invalid ingestion token."))

	parsed_readings = frappe.parse_json(readings) if readings else []
	if not isinstance(parsed_readings, list) or not parsed_readings:
		frappe.throw(_("readings must be a non-empty JSON array."))

	created = []
	updated = []

	for payload in parsed_readings:
		payload = frappe._dict(payload or {})
		doc = upsert_meter_reading(source, payload)
		if doc.flags.get("was_existing"):
			updated.append(doc.name)
		else:
			created.append(doc.name)

	frappe.db.set_value(
		"Energy Data Source",
		source.name,
		"last_payload_on",
		now_datetime(),
		update_modified=False,
	)
	frappe.db.commit()

	return {
		"status": "ok",
		"created_count": len(created),
		"updated_count": len(updated),
		"created": created,
		"updated": updated,
	}


def upsert_meter_reading(source, payload):
	meter = payload.get("energy_meter") or source.default_meter
	if not meter:
		frappe.throw(_("Each reading must include energy_meter or the source must define a default meter."))

	reading_datetime = payload.get("reading_datetime")
	if not reading_datetime:
		frappe.throw(_("Each reading must include reading_datetime."))

	if payload.get("closing_reading") in (None, ""):
		frappe.throw(_("Each reading must include closing_reading."))

	existing_name = get_existing_reading_name(source, payload, meter, reading_datetime)
	doc = (
		frappe.get_doc("Energy Meter Reading", existing_name)
		if existing_name
		else frappe.new_doc("Energy Meter Reading")
	)

	if existing_name:
		doc.flags.was_existing = True

	doc.ingestion_source = source.name
	doc.external_reference = payload.get("external_reference")
	doc.company = payload.get("company") or source.company or doc.company
	doc.energy_site = payload.get("energy_site") or source.default_energy_site or doc.energy_site
	doc.energy_meter = meter
	doc.reading_datetime = reading_datetime
	doc.reading_frequency = payload.get("reading_frequency") or source.ingestion_frequency or "Daily"
	doc.reading_source = payload.get("reading_source") or source.default_reading_source or "API"
	doc.opening_reading = payload.get("opening_reading", doc.opening_reading)
	doc.closing_reading = payload.get("closing_reading")
	doc.peak_demand = payload.get("peak_demand", doc.peak_demand)
	doc.power_factor = payload.get("power_factor", doc.power_factor)
	doc.rate = payload.get("rate", doc.rate)
	doc.notes = payload.get("notes", doc.notes)

	if existing_name:
		doc.save(ignore_permissions=True)
	else:
		doc.insert(ignore_permissions=True)

	return doc


def get_existing_reading_name(source, payload, meter, reading_datetime):
	if payload.get("external_reference"):
		existing = frappe.db.get_value(
			"Energy Meter Reading",
			{
				"ingestion_source": source.name,
				"external_reference": payload.get("external_reference"),
			},
		)
		if existing:
			return existing

	return frappe.db.get_value(
		"Energy Meter Reading",
		{
			"energy_meter": meter,
			"reading_datetime": reading_datetime,
		},
	)
