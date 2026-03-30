import math

import frappe
from frappe.utils import add_days, get_datetime, now_datetime

from inovis_ems.alerts import evaluate_reading_alerts


DEMO_PREFIX = "EMS-SHOWCASE"


def seed_showcase_data(company=None):
	company_doc = get_demo_company(company)
	project_name = get_demo_project(company_doc.name)
	asset_names = get_demo_assets(company_doc.name)

	cleanup_legacy_demo_rules(company_doc.name)
	configure_energy_settings(company_doc)
	sites = seed_sites(company_doc.name, project_name)
	meters = seed_meters(company_doc.name, sites, asset_names)
	sources = seed_data_sources(company_doc.name, sites, meters)
	seed_targets(company_doc.name, project_name, sites, meters)
	rules = seed_alert_rules(company_doc.name, sites, meters)

	purge_demo_transactions(list(meters), list(rules))
	summary = seed_readings(company_doc.name, sites, meters, sources)

	return {
		"company": company_doc.name,
		"sites": list(sites),
		"meters": list(meters),
		"sources": list(sources),
		"rules": list(rules),
		**summary,
	}


def get_demo_company(company=None):
	company_name = company or "Shelter For Life (Demo)"
	if frappe.db.exists("Company", company_name):
		return frappe.get_doc("Company", company_name)

	companies = frappe.get_all(
		"Company", fields=["name", "default_currency"], order_by="creation asc", limit=1
	)
	if not companies:
		frappe.throw("No Company found. Please create a Company before seeding showcase data.")

	return frappe.get_doc("Company", companies[0].name)


def get_demo_project(company):
	return frappe.db.get_value("Project", {"company": company}, "name")


def get_demo_assets(company):
	return frappe.get_all(
		"Asset",
		filters={"company": company},
		order_by="creation asc",
		pluck="name",
		limit=4,
	)


def configure_energy_settings(company_doc):
	settings = frappe.get_single("Energy Settings")
	settings.default_company = company_doc.name
	settings.default_currency = company_doc.default_currency or "USD"
	settings.carbon_emission_factor = 0.233
	settings.alert_threshold_percent = 15
	settings.baseline_months = 12
	settings.save(ignore_permissions=True)


def seed_sites(company, project_name):
	sites = {
		f"{DEMO_PREFIX} HQ Campus": {
			"site_name": f"{DEMO_PREFIX} HQ Campus",
			"company": company,
			"site_type": "Building",
			"is_active": 1,
			"floor_area": 4800,
			"floor_area_unit": "m2",
			"location": "Dar es Salaam HQ",
			"project": project_name,
			"notes": "Corporate office and admin block for showcase data.",
		},
		f"{DEMO_PREFIX} Production Plant": {
			"site_name": f"{DEMO_PREFIX} Production Plant",
			"company": company,
			"site_type": "Factory",
			"is_active": 1,
			"floor_area": 9200,
			"floor_area_unit": "m2",
			"location": "Coastal Industrial Zone",
			"project": project_name,
			"notes": "High-load manufacturing area with demand spikes.",
		},
		f"{DEMO_PREFIX} Solar Farm": {
			"site_name": f"{DEMO_PREFIX} Solar Farm",
			"company": company,
			"site_type": "Plant",
			"is_active": 1,
			"floor_area": 15000,
			"floor_area_unit": "m2",
			"location": "Makambako Solar Corridor",
			"project": project_name,
			"notes": "Distributed solar generation site for mixed-source reporting.",
		},
	}

	for site_name, payload in sites.items():
		upsert_named_doc("Energy Site", site_name, payload)

	return sites


def seed_meters(company, sites, asset_names):
	meters = {
		f"{DEMO_PREFIX} HQ Grid Meter": {
			"meter_name": f"{DEMO_PREFIX} HQ Grid Meter",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"meter_category": "Grid",
			"energy_source": "Electricity",
			"unit": "kWh",
			"default_rate": 0.18,
			"multiplier": 1,
			"is_active": 1,
			"asset": asset_names[0] if asset_names else None,
			"manufacturer": "Schneider Electric",
			"serial_number": f"{DEMO_PREFIX}-GRID-001",
		},
		f"{DEMO_PREFIX} Production Main Meter": {
			"meter_name": f"{DEMO_PREFIX} Production Main Meter",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} Production Plant",
			"meter_category": "Production Line",
			"energy_source": "Electricity",
			"unit": "kWh",
			"default_rate": 0.21,
			"multiplier": 1,
			"is_active": 1,
			"asset": asset_names[1] if len(asset_names) > 1 else None,
			"manufacturer": "Siemens",
			"serial_number": f"{DEMO_PREFIX}-PROD-001",
		},
		f"{DEMO_PREFIX} HVAC Meter": {
			"meter_name": f"{DEMO_PREFIX} HVAC Meter",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"meter_category": "HVAC",
			"energy_source": "Electricity",
			"unit": "kWh",
			"default_rate": 0.17,
			"multiplier": 1,
			"is_active": 1,
			"manufacturer": "ABB",
			"serial_number": f"{DEMO_PREFIX}-HVAC-001",
		},
		f"{DEMO_PREFIX} Solar Inverter Meter": {
			"meter_name": f"{DEMO_PREFIX} Solar Inverter Meter",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} Solar Farm",
			"meter_category": "Solar",
			"energy_source": "Solar",
			"unit": "kWh",
			"default_rate": 0.04,
			"multiplier": 1,
			"is_active": 1,
			"manufacturer": "Huawei",
			"serial_number": f"{DEMO_PREFIX}-SOLAR-001",
		},
	}

	for meter_name, payload in meters.items():
		upsert_named_doc("Energy Meter", meter_name, payload)

	return meters


def seed_data_sources(company, sites, meters):
	sources = {
		f"{DEMO_PREFIX} API Gateway": {
			"source_name": f"{DEMO_PREFIX} API Gateway",
			"company": company,
			"source_type": "API Push",
			"is_enabled": 1,
			"default_energy_site": f"{DEMO_PREFIX} HQ Campus",
			"default_meter": f"{DEMO_PREFIX} HQ Grid Meter",
			"ingestion_frequency": "Daily",
			"default_reading_source": "API",
			"authentication_token": "showcase-token-api-gateway",
			"notes": "Used for imported smart meter payloads in the showcase dataset.",
		},
		f"{DEMO_PREFIX} Solar SCADA": {
			"source_name": f"{DEMO_PREFIX} Solar SCADA",
			"company": company,
			"source_type": "IoT Gateway",
			"is_enabled": 1,
			"default_energy_site": f"{DEMO_PREFIX} Solar Farm",
			"default_meter": f"{DEMO_PREFIX} Solar Inverter Meter",
			"ingestion_frequency": "Daily",
			"default_reading_source": "IoT",
			"authentication_token": "showcase-token-solar-scada",
			"notes": "Simulates automated solar telemetry ingestion.",
		},
	}

	for source_name, payload in sources.items():
		upsert_named_doc("Energy Data Source", source_name, payload)

	return sources


def seed_targets(company, project_name, sites, meters):
	targets = {
		f"{DEMO_PREFIX} HQ Efficiency Target": {
			"target_name": f"{DEMO_PREFIX} HQ Efficiency Target",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"target_metric": "Consumption",
			"target_unit": "kWh",
			"improvement_goal_percent": 12,
			"is_active": 1,
			"baseline_from": add_days(now_datetime().date(), -120),
			"baseline_to": add_days(now_datetime().date(), -61),
			"target_from": add_days(now_datetime().date(), -60),
			"target_to": add_days(now_datetime().date(), 30),
			"target_value": 520,
			"notes": "Office efficiency target for the last 60-day operating window.",
		},
		f"{DEMO_PREFIX} Plant Peak Limit": {
			"target_name": f"{DEMO_PREFIX} Plant Peak Limit",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} Production Plant",
			"energy_meter": f"{DEMO_PREFIX} Production Main Meter",
			"target_metric": "Peak Demand",
			"target_unit": "kW",
			"improvement_goal_percent": 8,
			"is_active": 1,
			"baseline_from": add_days(now_datetime().date(), -120),
			"baseline_to": add_days(now_datetime().date(), -61),
			"target_from": add_days(now_datetime().date(), -60),
			"target_to": add_days(now_datetime().date(), 30),
			"target_value": 180,
			"notes": "Peak demand threshold for production load management.",
		},
	}

	for target_name, payload in targets.items():
		upsert_named_doc("Energy Performance Target", target_name, payload)


def seed_alert_rules(company, sites, meters):
	rules = {
		f"{DEMO_PREFIX} HQ High Consumption": {
			"rule_name": f"{DEMO_PREFIX} HQ High Consumption",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"energy_meter": f"{DEMO_PREFIX} HQ Grid Meter",
			"metric": "Consumption",
			"rule_type": "Static Threshold",
			"comparison": "Above",
			"threshold_value": 700,
			"lookback_readings": 3,
			"severity": "High",
			"notify_role": "Energy Manager",
			"is_enabled": 1,
			"notes": "Flags unusual office-grid spikes.",
		},
		f"{DEMO_PREFIX} Plant Peak Demand": {
			"rule_name": f"{DEMO_PREFIX} Plant Peak Demand",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} Production Plant",
			"energy_meter": f"{DEMO_PREFIX} Production Main Meter",
			"metric": "Peak Demand",
			"rule_type": "Static Threshold",
			"comparison": "Above",
			"threshold_value": 180,
			"lookback_readings": 3,
			"severity": "Critical",
			"notify_role": "Energy Manager",
			"is_enabled": 1,
			"notes": "Highlights demand-charge risk at the plant.",
		},
		f"{DEMO_PREFIX} HVAC Variance": {
			"rule_name": f"{DEMO_PREFIX} HVAC Variance",
			"company": company,
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"energy_meter": f"{DEMO_PREFIX} HVAC Meter",
			"metric": "Consumption",
			"rule_type": "Percentage Variance",
			"comparison": "Above",
			"threshold_value": 20,
			"lookback_readings": 5,
			"severity": "Medium",
			"notify_role": "Energy Analyst",
			"is_enabled": 1,
			"notes": "Catches abnormal HVAC drift versus recent history.",
		},
	}

	for rule_name, payload in rules.items():
		upsert_named_doc("Energy Alert Rule", rule_name, payload)

	return rules


def purge_demo_transactions(meter_names, rule_names):
	frappe.db.delete("Energy Alert", {"energy_meter": ["in", meter_names]})
	frappe.db.delete("Energy Meter Reading", {"energy_meter": ["in", meter_names]})


def cleanup_legacy_demo_rules(company):
	if frappe.db.exists("Energy Alert Rule", "rule1"):
		rule_company = frappe.db.get_value("Energy Alert Rule", "rule1", "company")
		if rule_company == company:
			frappe.db.delete("Energy Alert", {"energy_alert_rule": "rule1"})
			frappe.delete_doc("Energy Alert Rule", "rule1", ignore_permissions=True, force=True)


def seed_readings(company, sites, meters, sources):
	start_date = add_days(now_datetime().date(), -59)
	reading_count = 0
	open_alert_candidates = []

	for meter_name, config in get_meter_patterns().items():
		running_total = config["base_total"]
		for day_index in range(60):
			reading_date = add_days(start_date, day_index)
			consumption = build_consumption(config, day_index)
			peak_demand = build_peak_demand(config, day_index)
			running_total_next = running_total + consumption

			doc = frappe.get_doc(
				{
					"doctype": "Energy Meter Reading",
					"company": company,
					"energy_site": config["energy_site"],
					"energy_meter": meter_name,
					"ingestion_source": config.get("ingestion_source"),
					"external_reference": f"{meter_name}-{reading_date.isoformat()}",
					"reading_datetime": get_datetime(f"{reading_date} 08:00:00"),
					"reading_frequency": "Daily",
					"reading_source": config["reading_source"],
					"opening_reading": running_total,
					"closing_reading": running_total_next,
					"peak_demand": peak_demand,
					"power_factor": config["power_factor"],
					"rate": config["rate"],
					"notes": config["notes"],
				}
			).insert(ignore_permissions=True)

			running_total = running_total_next
			reading_count += 1
			if day_index == 59:
				open_alert_candidates.append(doc.name)

	for reading_name in open_alert_candidates:
		evaluate_reading_alerts(frappe.get_doc("Energy Meter Reading", reading_name))

	alert_count = frappe.db.count("Energy Alert", {"energy_meter": ["like", f"{DEMO_PREFIX}%"]})
	return {"reading_count": reading_count, "alert_count": alert_count}


def get_meter_patterns():
	return {
		f"{DEMO_PREFIX} HQ Grid Meter": {
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"ingestion_source": f"{DEMO_PREFIX} API Gateway",
			"reading_source": "API",
			"base_total": 145000,
			"rate": 0.18,
			"power_factor": 0.96,
			"notes": "Showcase office-grid meter history.",
			"base": 510,
			"amplitude": 55,
			"trend": 0.8,
			"anomaly_day": 59,
			"anomaly_value": 765,
			"peak_base": 102,
			"peak_amplitude": 8,
			"peak_anomaly": 142,
		},
		f"{DEMO_PREFIX} Production Main Meter": {
			"energy_site": f"{DEMO_PREFIX} Production Plant",
			"ingestion_source": f"{DEMO_PREFIX} API Gateway",
			"reading_source": "API",
			"base_total": 265000,
			"rate": 0.21,
			"power_factor": 0.91,
			"notes": "Showcase production demand profile.",
			"base": 890,
			"amplitude": 85,
			"trend": 1.2,
			"anomaly_day": 59,
			"anomaly_value": 1040,
			"peak_base": 156,
			"peak_amplitude": 12,
			"peak_anomaly": 224,
		},
		f"{DEMO_PREFIX} HVAC Meter": {
			"energy_site": f"{DEMO_PREFIX} HQ Campus",
			"reading_source": "Manual",
			"base_total": 64000,
			"rate": 0.17,
			"power_factor": 0.94,
			"notes": "Showcase HVAC sub-meter with end-of-period anomaly.",
			"base": 205,
			"amplitude": 18,
			"trend": 0.25,
			"anomaly_day": 59,
			"anomaly_value": 315,
			"peak_base": 44,
			"peak_amplitude": 3,
			"peak_anomaly": 61,
		},
		f"{DEMO_PREFIX} Solar Inverter Meter": {
			"energy_site": f"{DEMO_PREFIX} Solar Farm",
			"ingestion_source": f"{DEMO_PREFIX} Solar SCADA",
			"reading_source": "IoT",
			"base_total": 84000,
			"rate": 0.04,
			"power_factor": 1.0,
			"notes": "Showcase solar telemetry profile.",
			"base": 460,
			"amplitude": 65,
			"trend": 0.4,
			"anomaly_day": None,
			"anomaly_value": None,
			"peak_base": 0,
			"peak_amplitude": 0,
			"peak_anomaly": 0,
		},
	}


def build_consumption(config, day_index):
	if config.get("anomaly_day") == day_index:
		return config["anomaly_value"]

	return round(
		config["base"]
		+ (math.sin(day_index / 4.2) * config["amplitude"])
		+ (day_index * config["trend"]),
		2,
	)


def build_peak_demand(config, day_index):
	if config.get("anomaly_day") == day_index:
		return config["peak_anomaly"]

	return round(config["peak_base"] + abs(math.cos(day_index / 5.1) * config["peak_amplitude"]), 2)


def upsert_named_doc(doctype, name, payload):
	payload = {k: v for k, v in payload.items() if v is not None}
	if frappe.db.exists(doctype, name):
		doc = frappe.get_doc(doctype, name)
		doc.update(payload)
		doc.save(ignore_permissions=True)
		return doc

	doc = frappe.get_doc({"doctype": doctype, **payload})
	doc.insert(ignore_permissions=True)
	return doc
