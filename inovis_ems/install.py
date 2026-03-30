import json
from pathlib import Path

import frappe

from inovis_ems.custom_fields import create_erpnext_custom_fields


EMS_ROLES = ("Energy Manager", "Energy Analyst")


def after_install():
	create_roles()
	create_erpnext_custom_fields()
	sync_workspace()


def create_roles():
	for role in EMS_ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc(
				{
					"doctype": "Role",
					"role_name": role,
					"desk_access": 1,
					"is_custom": 1,
				}
			).insert(ignore_permissions=True)

	frappe.clear_cache()


def sync_workspace():
	workspace_path = (
		Path(__file__).resolve().parent
		/ "inovis_ems"
		/ "workspace"
		/ "inovis_ems"
		/ "inovis_ems.json"
	)
	data = json.loads(workspace_path.read_text())
	for fieldname in ("creation", "modified", "modified_by", "owner", "idx", "docstatus"):
		data.pop(fieldname, None)

	if frappe.db.exists("Workspace", data["name"]):
		doc = frappe.get_doc("Workspace", data["name"])
		doc.update(data)
	else:
		doc = frappe.get_doc(data)

	doc.save(ignore_permissions=True)
