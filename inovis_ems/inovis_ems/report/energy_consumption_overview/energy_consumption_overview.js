frappe.query_reports["Energy Consumption Overview"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
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
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: ["Monthly", "Weekly", "Daily"],
			default: "Monthly",
		},
	],
};
