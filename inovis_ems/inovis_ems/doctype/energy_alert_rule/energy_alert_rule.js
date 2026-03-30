frappe.ui.form.on("Energy Alert Rule", {
	setup(frm) {
		frm.set_query("energy_site", () => ({
			filters: frm.doc.company ? { company: frm.doc.company } : {},
		}));

		frm.set_query("energy_meter", () => {
			const filters = {};
			if (frm.doc.company) filters.company = frm.doc.company;
			if (frm.doc.energy_site) filters.energy_site = frm.doc.energy_site;
			return { filters };
		});
	},
});
