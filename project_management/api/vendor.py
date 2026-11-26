
import frappe
from frappe import _

from project_management.api.portal import (
    get_current_portal_user
)


def get_vendor_projects(user):
    memberships = frappe.get_all(
        "Project Vendor Member",
        filters={
            "user": user,
            "parenttype": "Project",
            "parentfield": "project_vendor_members"
        },
        fields=["parent"],
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
            "end_date",
            "description"
        ],
        order_by="creation desc",
        page_length=1000
    )

    return projects


@frappe.whitelist()
def get_dashboard():
    user = get_current_portal_user("Project Vendor")

    projects = get_vendor_projects(user)

    project_names = [
        project.name for project in projects
    ]

    if not project_names:
        return {
            "summary": {
                "total_projects": 0,
                "total_tasks": 0,
                "completed_tasks": 0,
                "total_deliverables": 0
            },
            "projects": [],
            "tasks": [],
            "deliverables": []
        }

    task_filters = {
        "project": ["in", project_names],
        "assigned_to": user
    }

    total_tasks = frappe.db.count(
        "Task",
        filters=task_filters
    )

    completed_tasks = frappe.db.count(
        "Task",
        filters={
            "project": ["in", project_names],
            "assigned_to": user,
            "status": "Completed"
        }
    )

    deliverable_filters = {
        "project": ["in", project_names],
        "submitted_by": user
    }

    total_deliverables = frappe.db.count(
        "Deliverable",
        filters=deliverable_filters
    )

    tasks = frappe.get_all(
        "Task",
        filters=task_filters,
        fields=[
            "name",
            "task_title",
            "project",
            "status",
            "start_date",
            "due_date",
            "progress"
        ],
        order_by="modified desc",
        page_length=10
    )

    deliverables = frappe.get_all(
        "Deliverable",
        filters=deliverable_filters,
        fields=[
            "name",
            "project",
            "deliverable_name",
            "status",
            "submitted_on",
            "file",
            "client_feedback"
        ],
        order_by="modified desc",
        page_length=10
    )

    return {
        "summary": {
            "total_projects": len(projects),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "total_deliverables": total_deliverables
        },
        "projects": projects,
        "tasks": tasks,
        "deliverables": deliverables
    }


@frappe.whitelist()
def get_project_details(project_name: str):
    user = get_current_portal_user("Project Vendor")

    projects = get_vendor_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this project."),
            frappe.PermissionError
        )

    project = frappe.get_doc("Project", project_name)

    tasks = frappe.get_all(
        "Task",
        filters={
            "project": project_name,
            "assigned_to": user
        },
        fields=[
            "name",
            "task_title",
            "description",
            "assigned_to",
            "status",
            "start_date",
            "due_date",
            "progress"
        ],
        order_by="creation asc"
    )

    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": project_name,
            "submitted_by": user
        },
        fields=[
            "name",
            "deliverable_name",
            "description",
            "status",
            "submitted_on",
            "file",
            "client_feedback",
            "reviewed_by",
            "reviewed_on"
        ],
        order_by="creation desc"
    )

    return {
        "project": {
            "name": project.name,
            "project_name": project.project_name,
            "client": project.client,
            "status": project.status,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "description": project.description
        },
        "tasks": tasks,
        "deliverables": deliverables
    }


@frappe.whitelist(methods=["POST"])
def submit_deliverable(
    project_name,
    deliverable_name,
    description,
    file_url
):
    user = get_current_portal_user("Project Vendor")

    projects = get_vendor_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this project."),
            frappe.PermissionError
        )

    if not deliverable_name or not deliverable_name.strip():
        frappe.throw(_("Please enter a deliverable name."))

    if not file_url:
        frappe.throw(_("Please upload a file."))

    file_name = frappe.db.get_value(
        "File",
        {
            "file_url": file_url,
            "owner": user
        },
        "name"
    )

    if not file_name:
        frappe.throw(
            _("Uploaded file not found or access denied.")
        )

    deliverable = frappe.get_doc({
        "doctype": "Deliverable",
        "project": project_name,
        "deliverable_name": deliverable_name.strip(),
        "description": description,
        "file": file_url,
        "submitted_by": user,
        "submitted_on": frappe.utils.now_datetime(),
        "status": "Submitted"
    })

    deliverable.insert(ignore_permissions=True)

    frappe.db.set_value(
        "File",
        file_name,
        {
            "attached_to_doctype": "Deliverable",
            "attached_to_name": deliverable.name,
            "attached_to_field": "file"
        }
    )
    return {
        "success": True,
        "message": _("Deliverable submitted successfully."),
        "deliverable": deliverable.name
    }
