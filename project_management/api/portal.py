
import frappe
from frappe import _


@frappe.whitelist()
def get_portal_session():
    user = frappe.session.user

    if user == "Guest":
        return {
            "logged_in": False,
            "user": None,
            "role": None
        }

    roles = frappe.get_roles(user)

    if "Project Client" in roles:
        portal_role = "client"

    elif "Project Vendor" in roles:
        portal_role = "vendor"

    else:
        portal_role = "unauthorized"

    return {
        "logged_in": True,
        "user": user,
        "role": portal_role
    }


def get_current_portal_user(required_role):
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(
            _("Please login to continue."),
            frappe.PermissionError
        )

    roles = frappe.get_roles(user)

    if required_role not in roles:
        frappe.throw(
            _("You do not have permission to access this portal."),
            frappe.PermissionError
        )

    return user


def get_client_projects(user):
    memberships = frappe.get_all(
        "Project Client Member",
        filters={
            "user": user,
            "parenttype": "Project",
            "parentfield": "project_client_members"
        },
        fields=["parent", "client"],
        page_length=10000
    )

    project_names = list(set([
        member.parent for member in memberships
    ]))

    if not project_names:
        return []

    projects = frappe.get_all(
        "Project",
        filters={
            "name": ["in", project_names]
        },
        fields=[
            "name",
            "project_name",
            "client",
            "status",
            "start_date",
            "end_date"
        ],
        page_length=1000
    )

    valid_projects = []

    for project in projects:
        for member in memberships:
            if (
                member.parent == project.name
                and member.client == project.client
            ):
                valid_projects.append(project)
                break

    return valid_projects
