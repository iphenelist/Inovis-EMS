frappe.ui.form.on("Energy Data Source", {
	setup(frm) {
		frm.set_query("default_energy_site", () => ({
			filters: frm.doc.company ? { company: frm.doc.company } : {},
		}));

		frm.set_query("default_meter", () => {
			const filters = {};
			if (frm.doc.company) filters.company = frm.doc.company;
			if (frm.doc.default_energy_site) filters.energy_site = frm.doc.default_energy_site;
			return { filters };
		});
	},
	refresh(frm) {
		if (!frm.doc.name || !frm.doc.authentication_token) return;
		frm.dashboard.set_headline(
			__("API Method: {0}", ["`/api/method/inovis_ems.api.ingest_meter_readings`"])
		);
	},
});
