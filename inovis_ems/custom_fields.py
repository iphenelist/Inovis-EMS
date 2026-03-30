from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_erpnext_custom_fields():
	custom_fields = {
		"Purchase Invoice": [
			{
				"fieldname": "ems_section_break",
				"fieldtype": "Section Break",
				"label": "Energy Management",
				"insert_after": "remarks",
				"collapsible": 1,
				"allow_on_submit": 1,
			},
			{
				"fieldname": "is_energy_invoice",
				"fieldtype": "Check",
				"label": "Energy Invoice",
				"insert_after": "ems_section_break",
				"default": "0",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_site",
				"fieldtype": "Link",
				"label": "Energy Site",
				"options": "Energy Site",
				"insert_after": "is_energy_invoice",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_meter",
				"fieldtype": "Link",
				"label": "Energy Meter",
				"options": "Energy Meter",
				"insert_after": "energy_site",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_data_source",
				"fieldtype": "Link",
				"label": "Energy Data Source",
				"options": "Energy Data Source",
				"insert_after": "energy_meter",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_column_break",
				"fieldtype": "Column Break",
				"insert_after": "energy_data_source",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_service_period_from",
				"fieldtype": "Date",
				"label": "Energy Service Period From",
				"insert_after": "energy_column_break",
				"allow_on_submit": 1,
			},
			{
				"fieldname": "energy_service_period_to",
				"fieldtype": "Date",
				"label": "Energy Service Period To",
				"insert_after": "energy_service_period_from",
				"allow_on_submit": 1,
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
