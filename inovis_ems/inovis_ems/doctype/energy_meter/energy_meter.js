frappe.ui.form.on("Energy Meter", {
	setup(frm) {
		frm.set_query("energy_site", () => ({
			filters: frm.doc.company ? { company: frm.doc.company } : {},
		}));
	},
	energy_site(frm) {
		if (!frm.doc.energy_site || frm.doc.company) return;

		frappe.db.get_value("Energy Site", frm.doc.energy_site, "company").then(({ message }) => {
			if (message?.company) {
				frm.set_value("company", message.company);
			}
		});
	},
});
