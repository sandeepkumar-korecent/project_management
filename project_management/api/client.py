
import frappe
from frappe import _
from frappe.utils import validate_email_address

from project_management.api.portal import (
    get_current_portal_user,
    get_client_projects
)


@frappe.whitelist()
def get_dashboard():
    user = get_current_portal_user("Project Client")

    projects = get_client_projects(user)

    project_names = [
        project.name for project in projects
    ]

    total_tasks = 0
    completed_tasks = 0
    tasks = []
    deliverables = []

    if project_names:
        total_tasks = frappe.db.count(
            "Task",
            filters={
                "project": ["in", project_names]
            }
        )

        completed_tasks = frappe.db.count(
            "Task",
            filters={
                "project": ["in", project_names],
                "status": "Completed"
            }
        )

        tasks = frappe.get_all(
            "Task",
            filters={
                "project": ["in", project_names]
            },
            fields=[
                "name",
                "task_title",
                "project",
                "status",
                "due_date",
                "progress"
            ],
            order_by="modified desc",
            page_length=10
        )

        deliverables = frappe.get_all(
            "Deliverable",
            filters={
                "project": ["in", project_names]
            },
            fields=[
                "name",
                "deliverable_name",
                "project",
                "status",
                "submitted_on"
            ],
            order_by="modified desc",
            page_length=10
        )

    pending_tasks = total_tasks - completed_tasks

    return {
        "total_projects": len(projects),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "projects": projects,
        "tasks": tasks,
        "deliverables": deliverables
    }


@frappe.whitelist()
def get_project_details(project_name: str):
    user = get_current_portal_user("Project Client")

    projects = get_client_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this Project."),
            frappe.PermissionError
        )

    project = frappe.get_doc("Project", project_name)

    tasks = frappe.get_all(
        "Task",
        filters={
            "project": project_name
        },
        fields=[
            "name",
            "task_title",
            "status",
            "start_date",
            "due_date",
            "progress"
        ],
        order_by="due_date asc",
        page_length=100
    )

    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": project_name
        },
        fields=[
            "name",
            "deliverable_name",
            "status",
            "submitted_on",
            "file",
            "client_feedback"
        ],
        order_by="modified desc",
        page_length=100
    )


    client_members = frappe.get_all(
        "Project Client Member",
        filters={
            "parent": project_name,
            "parenttype": "Project",
            "parentfield": "project_client_members"
        },
        fields=["user", "client"],
        page_length=100
    )

    for member in client_members:
        member["full_name"] = frappe.db.get_value(
            "User",
            member.user,
            "full_name"
        )

    members = frappe.get_all(
        "Project Client Member",
        filters={
            "parent": project_name,
            "parenttype": "Project",
            "parentfield": "project_client_members"
        },
        fields=[
            "user",
            "client"
        ],
        order_by="idx asc"
    )

    for member in members:
        member["full_name"] = frappe.db.get_value(
            "User",
            member.user,
            "full_name"
        ) or member.user

    return {
        "project": {
            "name": project.name,
            "project_name": project.project_name,
            "client": project.client,
            "status": project.status,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "description": project.description,
            "client_members": client_members

        },
        "tasks": tasks,
        "deliverables": deliverables,
        "members": members
    }


    


@frappe.whitelist()
def review_deliverable(deliverable_name, decision, feedback=None):
    user = get_current_portal_user("Project Client")

    if decision not in ["Accepted", "Changes Requested"]:
        frappe.throw(_("Invalid review decision."))

    if not frappe.db.exists("Deliverable", deliverable_name):
        frappe.throw(_("Deliverable not found."))

    deliverable = frappe.get_doc("Deliverable", deliverable_name)

    projects = get_client_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if deliverable.project not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this Deliverable."),
            frappe.PermissionError
        )

    if deliverable.status != "Submitted":
        frappe.throw(
            _("Only submitted deliverables can be reviewed.")
        )

    if decision == "Changes Requested" and not (feedback or "").strip():
        frappe.throw(
            _("Please provide feedback when requesting changes.")
        )

    frappe.db.set_value(
        "Deliverable",
        deliverable_name,
        {
            "status": decision,
            "client_feedback": (feedback or "").strip(),
            "reviewed_by": user,
            "reviewed_on": frappe.utils.now_datetime()
        }
    )

    return {
        "success": True,
        "message": _("Deliverable review saved successfully.")
    }


@frappe.whitelist(methods=["POST"])
def invite_client_member(project_name, full_name, email):
    current_user = get_current_portal_user("Project Client")

    projects = get_client_projects(current_user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this Project."),
            frappe.PermissionError
        )

    full_name = (full_name or "").strip()
    email = (email or "").strip().lower()

    if not full_name:
        frappe.throw(_("Please enter the member's name."))

    if not email:
        frappe.throw(_("Please enter the member's email address."))

    validate_email_address(email, throw=True)

    if not frappe.db.exists("Role", "Project Client"):
        frappe.throw(
            _("Project Client role does not exist. Please create it first.")
        )

    project = frappe.get_doc("Project", project_name)
    for member in project.project_client_members:
        if member.user == email:
            frappe.throw(
                _("This user is already a member of this project.")
            )

    user_exists = frappe.db.exists("User", email)

    if user_exists:
        invited_user = frappe.get_doc("User", email)
        if invited_user.user_type != "Website User":
            frappe.throw(
                _("This email already belongs to an internal System User.")
            )

        if not invited_user.enabled:
            frappe.throw(
                _("This user account is disabled. Please contact the administrator.")
            )

        existing_roles = frappe.get_roles(email)

        if any(
            role in existing_roles
            for role in [
                "Project Vendor",
                "Project Manager",
                "System Manager"
            ]
        ):
            frappe.throw(
                _("This account has an incompatible role and cannot be invited as a Client Member.")
            )

        if "Project Client" not in existing_roles:
            invited_user.append(
                "roles",
                {"role": "Project Client"}
            )
            invited_user.save(ignore_permissions=True)

        account_created = False

    else:
        name_parts = full_name.split(" ", 1)

        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        invited_user = frappe.new_doc("User")

        invited_user.update({
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 1
        })

        invited_user.append(
            "roles",
            {"role": "Project Client"}
        )

        invited_user.insert(ignore_permissions=True)

        account_created = True

    project.append(
        "project_client_members",
        {
            "user": email,
            "client": project.client
        }
    )

    project.save(ignore_permissions=True)

    frappe.sendmail(
        recipients=[email],
        subject=_("Invitation to Project: {0}").format(project.project_name),
        message=_(
            "Hello {0},<br><br>"
            "You have been added as a Client Member to the project "
            "<b>{1}</b>.<br><br>"
            "You can log in to the Project Management Portal to view "
            "project progress and share feedback.<br><br>"
            "Regards,<br>"
            "Project Management Team"
        ).format(
            frappe.utils.escape_html(full_name),
            frappe.utils.escape_html(project.project_name)
        )
    )

    return {
        "success": True,
        "account_created": account_created,
        "email": email,
        "message": _("Client member invited successfully.")
    }



@frappe.whitelist()
def get_comments(reference_doctype, reference_name):
    user = get_current_portal_user("Project Client")

    if reference_doctype == "Project":
        project_name = reference_name

    elif reference_doctype == "Task":
        project_name = frappe.db.get_value(
            "Task",
            reference_name,
            "project"
        )

        if not project_name:
            frappe.throw(_("Task not found."))

    else:
        frappe.throw(_("Invalid document type."))

    projects = get_client_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this project."),
            frappe.PermissionError
        )

    comments = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "comment_type": "Comment"
        },
        fields=[
            "name",
            "content",
            "comment_by",
            "creation"
        ],
        order_by="creation asc"
    )

    for comment in comments:
        comment["full_name"] = frappe.db.get_value(
            "User",
            comment.comment_by,
            "full_name"
        ) or comment.comment_by

    return comments


@frappe.whitelist(methods=["POST"])
def add_comment(reference_doctype, reference_name, content):
    user = get_current_portal_user("Project Client")

    content = (content or "").strip()

    if not content:
        frappe.throw(_("Please enter a comment."))
    if reference_doctype == "Project":
        project_name = reference_name

    elif reference_doctype == "Task":
        project_name = frappe.db.get_value(
            "Task",
            reference_name,
            "project"
        )

        if not project_name:
            frappe.throw(_("Task not found."))

    else:
        frappe.throw(_("Invalid document type."))

    projects = get_client_projects(user)

    allowed_project_names = [
        project.name for project in projects
    ]

    if project_name not in allowed_project_names:
        frappe.throw(
            _("You do not have access to this project."),
            frappe.PermissionError
        )

    comment = frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
        "content": content
    })

    comment.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": _("Comment added successfully.")
    }
