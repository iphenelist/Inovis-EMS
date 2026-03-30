frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		frm.set_query("energy_site", () => ({
			filters: { is_active: 1 },
		}));

		frm.set_query("energy_meter", () => ({
			filters: {
				is_active: 1,
				...(frm.doc.energy_site ? { energy_site: frm.doc.energy_site } : {}),
			},
		}));

		frm.set_query("energy_data_source", () => ({
			filters: {
				is_enabled: 1,
				...(frm.doc.energy_site ? { default_energy_site: frm.doc.energy_site } : {}),
			},
		}));
	},
	energy_site(frm) {
		if (frm.doc.energy_site) {
			frm.set_value("is_energy_invoice", 1);
		}
	},
	energy_meter(frm) {
		if (!frm.doc.energy_meter) {
			return;
		}

		frm.set_value("is_energy_invoice", 1);

		if (!frm.doc.energy_site) {
			frappe.db.get_value("Energy Meter", frm.doc.energy_meter, "energy_site").then((r) => {
				if (r.message?.energy_site) {
					frm.set_value("energy_site", r.message.energy_site);
				}
			});
		}
	},
	energy_data_source(frm) {
		if (frm.doc.energy_data_source) {
			frm.set_value("is_energy_invoice", 1);
		}
	},
});
