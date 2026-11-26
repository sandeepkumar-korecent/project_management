
import frappe

def get_user_roles(user=None):
    if not user:
        user = frappe.session.user
    return frappe.get_roles(user)

def is_admin(user=None):
    if not user:
        user = frappe.session.user
    if user == "Administrator":
        return True
    if "System Manager" in get_user_roles(user):
        return True
    return False

def is_project_manager(project_name, user=None):
    if not user:
        user = frappe.session.user
    manager = frappe.db.get_value(
        "Project",
        project_name,
        "project_manager"
    )
    if manager == user:
        return True
    return False

def is_project_team_member(project_name, user=None):
    if not user:
        user = frappe.session.user
    member = frappe.db.exists(
        "Project Team Member",
        {
            "parent": project_name,
            "parenttype": "Project",
            "parentfield": "project_team_members",
            "user": user
        }
    )
    if member:
        return True
    return False
