frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Monthly Energy Consumption"] = {
	method: "inovis_ems.inovis_ems.dashboard_chart_source.monthly_energy_consumption.monthly_energy_consumption.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "energy_site",
			label: __("Energy Site"),
			fieldtype: "Link",
			options: "Energy Site",
		},
		{
			fieldname: "energy_meter",
			label: __("Energy Meter"),
			fieldtype: "Link",
			options: "Energy Meter",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -11),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
