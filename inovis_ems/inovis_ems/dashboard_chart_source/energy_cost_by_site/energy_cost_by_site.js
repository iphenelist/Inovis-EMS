frappe.provide("frappe.dashboards.chart_sources");

frappe.dashboards.chart_sources["Energy Cost by Site"] = {
	method: "inovis_ems.inovis_ems.dashboard_chart_source.energy_cost_by_site.energy_cost_by_site.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -2),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
	],
};
