
import frappe
from frappe import _

from raven.api.chat_stream import get_messages
from raven.api.raven_message import send_message


def get_project_channel(project_name):
    user = frappe.session.user

    if user == "Guest":
        frappe.throw(_("Please login to continue."), frappe.PermissionError)

    if not frappe.db.exists("Project", project_name):
        frappe.throw(_("Project does not exist."))

    roles = frappe.get_roles(user)

    if "Project Client" in roles:
        member_doctype = "Project Client Member"
        channel_name = "discussion"
        parentfield = "project_client_members"

    elif "Project Vendor" in roles:
        member_doctype = "Project Vendor Member"
        channel_name = "external"
        parentfield = "project_vendor_members"

    else:
        frappe.throw(
            _("You do not have permission to access project discussions."),
            frappe.PermissionError
        )

    is_project_member = frappe.db.exists(
        member_doctype,
        {
            "parent": project_name,
            "parenttype": "Project",
            "parentfield": parentfield,
            "user": user
        }
    )

    if not is_project_member:
        frappe.throw(
            _("You are not a member of this project."),
            frappe.PermissionError
        )

    workspace_name = "Project " + project_name

    if not frappe.db.exists("Raven Workspace", workspace_name):
        frappe.throw(_("Project discussion workspace not found."))

    channel = frappe.db.get_value(
        "Raven Channel",
        {
            "workspace": workspace_name,
            "channel_name": channel_name
        },
        "name"
    )

    if not channel:
        frappe.throw(_("Project discussion channel not found."))

    is_channel_member = frappe.db.exists(
        "Raven Channel Member",
        {
            "channel_id": channel,
            "user_id": user
        }
    )

    if not is_channel_member:
        frappe.throw(
            _("You are not a member of this discussion channel."),
            frappe.PermissionError
        )

    return channel


@frappe.whitelist()
def get_project_discussion(project_name:str):
    channel = get_project_channel(project_name)

    result = get_messages(
        channel_id=channel,
        limit=30,
        update_last_visit=False
    )

    messages = result.get("messages", [])

    users = set(
        message.get("owner")
        for message in messages
        if message.get("owner")
    )

    user_names = {}

    if users:
        user_records = frappe.get_all(
            "User",
            filters={"name": ["in", list(users)]},
            fields=["name", "full_name"]
        )

        user_names = {
            user.name: user.full_name
            for user in user_records
        }

    for message in messages:
        message["full_name"] = user_names.get(
            message.get("owner"),
            message.get("owner")
        )

    return {
        "messages": messages,
        "has_old_messages": result.get("has_old_messages", False)
    }


@frappe.whitelist(methods=["POST"])
def send_project_message(project_name : str, message : str):
    channel = get_project_channel(project_name)

    message = (message or "").strip()

    if not message:
        frappe.throw(_("Please enter a message."))

    result = send_message(
        channel_id=channel,
        text=message
    )

    return {
        "name": result.name,
        "owner": result.owner,
        "full_name": frappe.db.get_value(
            "User", result.owner, "full_name"
        ) or result.owner,
        "creation": result.creation,
        "text": result.text,
        "channel_id": result.channel_id
    }
