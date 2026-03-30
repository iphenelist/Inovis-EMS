frappe.ui.form.on("Energy Meter Reading", {
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

		frm.set_query("ingestion_source", () => ({
			filters: frm.doc.company ? { company: frm.doc.company } : {},
		}));
	},
	energy_meter(frm) {
		if (!frm.doc.energy_meter) return;

		frappe.db
			.get_value(
				"Energy Meter",
				frm.doc.energy_meter,
				["company", "energy_site", "unit", "default_rate", "multiplier"]
			)
			.then(({ message }) => {
				if (!message) return;
				if (message.company) frm.set_value("company", message.company);
				if (message.energy_site) frm.set_value("energy_site", message.energy_site);
				if (message.unit) frm.set_value("unit", message.unit);
				if (message.default_rate) frm.set_value("rate", message.default_rate);
				if (message.multiplier) frm.set_value("multiplier", message.multiplier);
			});
	},
});
