
import frappe
from raven.api.raven_users import give_raven_access


def get_project_members(project):
    # Project Manager and internal team members
    internal_members = set()

    if project.project_manager:
        internal_members.add(project.project_manager)

    for member in project.project_team_members:
        if member.user:
            internal_members.add(member.user)

    # Vendor members
    vendor_members = set()

    for member in project.project_vendor_members:
        if member.user:
            vendor_members.add(member.user)

    # Client members
    client_members = set()

    for member in project.project_client_members:
        if member.user:
            client_members.add(member.user)

    # Members of each Raven channel
    channel_members = {
        "internal": internal_members,
        "external": internal_members | vendor_members,
        "discussion": internal_members | client_members
    }

    # All members who should access the workspace
    workspace_members = (
        internal_members | vendor_members | client_members
    )

    return workspace_members, channel_members


def give_raven_access_to_members(users):
    if not users:
        return

    for user in users:
        raven_user_exists = frappe.db.exists(
            "Raven User",
            user
        )

        raven_role_exists = frappe.db.exists(
            "Has Role",
            {
                "parent": user,
                "role": "Raven User"
            }
        )

        # Give access if the Raven User or its role is missing
        if not raven_user_exists or not raven_role_exists:
            user_doc = frappe.get_doc("User", user)
            give_raven_access(user_doc)


def get_or_create_workspace(project):
    workspace_name = "Project " + project.name

    if frappe.db.exists("Raven Workspace", workspace_name):
        return workspace_name

    workspace = frappe.get_doc({
        "doctype": "Raven Workspace",
        "workspace_name": workspace_name,
        "type": "Private",
        "description": "Private workspace for Project " + project.name,
        "owner": project.project_manager
    })

    workspace.insert(ignore_permissions=True)

    return workspace.name


def sync_workspace_members(workspace, users, project_manager):
    existing_members = frappe.get_all(
        "Raven Workspace Member",
        filters={
            "workspace": workspace
        },
        fields=[
            "name",
            "user",
            "is_admin"
        ]
    )

    existing_users = {
        member.user: member
        for member in existing_members
    }

    # Add Project Manager first
    new_users = users - set(existing_users)

    sorted_new_users = sorted(
        new_users,
        key=lambda user: user != project_manager
    )

    for user in sorted_new_users:
        frappe.get_doc({
            "doctype": "Raven Workspace Member",
            "workspace": workspace,
            "user": user,
            "is_admin": 1 if user == project_manager else 0
        }).insert(ignore_permissions=True)

    # Refresh members after adding new users
    current_members = frappe.get_all(
        "Raven Workspace Member",
        filters={
            "workspace": workspace
        },
        fields=[
            "name",
            "user",
            "is_admin"
        ]
    )

    # Make Project Manager an admin first
    for member in current_members:
        if (
            member.user == project_manager
            and not member.is_admin
        ):
            member_doc = frappe.get_doc(
                "Raven Workspace Member",
                member.name
            )

            member_doc.is_admin = 1
            member_doc.save(ignore_permissions=True)

    # Remove admin status from other members
    for member in current_members:
        if (
            member.user != project_manager
            and member.is_admin
        ):
            member_doc = frappe.get_doc(
                "Raven Workspace Member",
                member.name
            )

            member_doc.is_admin = 0
            member_doc.save(ignore_permissions=True)

    # Remove members who are no longer part of the project
    existing_users = {
        member.user: member
        for member in current_members
    }

    removed_users = set(existing_users) - users

    for user in removed_users:
        member_doc = frappe.get_doc(
            "Raven Workspace Member",
            existing_users[user].name
        )

        member_doc.delete(ignore_permissions=True)


def get_or_create_channel(workspace, channel_name):
    channel = frappe.db.get_value(
        "Raven Channel",
        {
            "workspace": workspace,
            "channel_name": channel_name
        },
        "name"
    )

    if channel:
        return channel

    channel_doc = frappe.get_doc({
        "doctype": "Raven Channel",
        "channel_name": channel_name,
        "type": "Private",
        "workspace": workspace
    })

    channel_doc.flags.do_not_add_member = True
    channel_doc.flags.ignore_channel_member_check = True

    channel_doc.insert(ignore_permissions=True)

    return channel_doc.name


def sync_channel_members(channel, users, project_manager):
    existing_members = frappe.get_all(
        "Raven Channel Member",
        filters={
            "channel_id": channel
        },
        fields=[
            "name",
            "user_id",
            "is_admin"
        ]
    )

    existing_users = {
        member.user_id: member
        for member in existing_members
    }

    # Add Project Manager first
    new_users = users - set(existing_users)

    sorted_new_users = sorted(
        new_users,
        key=lambda user: user != project_manager
    )

    for user in sorted_new_users:
        frappe.get_doc({
            "doctype": "Raven Channel Member",
            "channel_id": channel,
            "user_id": user,
            "is_admin": 1 if user == project_manager else 0
        }).insert(ignore_permissions=True)

    # Refresh channel members
    current_members = frappe.get_all(
        "Raven Channel Member",
        filters={
            "channel_id": channel
        },
        fields=[
            "name",
            "user_id",
            "is_admin"
        ]
    )

    # Make Project Manager an admin first
    for member in current_members:
        if (
            member.user_id == project_manager
            and not member.is_admin
        ):
            member_doc = frappe.get_doc(
                "Raven Channel Member",
                member.name
            )

            member_doc.is_admin = 1
            member_doc.save(ignore_permissions=True)

    # Other members should not be admins
    for member in current_members:
        if (
            member.user_id != project_manager
            and member.is_admin
        ):
            member_doc = frappe.get_doc(
                "Raven Channel Member",
                member.name
            )

            member_doc.is_admin = 0
            member_doc.save(ignore_permissions=True)

    # Remove members who are no longer part of this channel
    existing_users = {
        member.user_id: member
        for member in current_members
    }

    removed_users = set(existing_users) - users

    for user in removed_users:
        member_doc = frappe.get_doc(
            "Raven Channel Member",
            existing_users[user].name
        )

        member_doc.delete(ignore_permissions=True)


def sync_project_raven(doc, method=None):
    if not doc.project_manager:
        return

    # Get all required project members
    workspace_members, channel_members = get_project_members(doc)

    # Give Raven access to all project members
    give_raven_access_to_members(workspace_members)

    # Create or get project workspace
    workspace = get_or_create_workspace(doc)

    # Update workspace owner
    frappe.db.set_value(
        "Raven Workspace",
        workspace,
        "owner",
        doc.project_manager
    )

    # Synchronize workspace members
    sync_workspace_members(
        workspace,
        workspace_members,
        doc.project_manager
    )

    # Create and synchronize all three channels
    for channel_name, users in channel_members.items():
        channel = get_or_create_channel(
            workspace,
            channel_name
        )

        sync_channel_members(
            channel,
            users,
            doc.project_manager
        )


def delete_project_raven_workspace(doc, method=None):
    workspace_name = "Project " + doc.name

    if frappe.db.exists("Raven Workspace", workspace_name):
        frappe.delete_doc(
            "Raven Workspace",
            workspace_name,
            ignore_permissions=True
        )
