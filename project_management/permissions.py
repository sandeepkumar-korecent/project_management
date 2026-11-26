
import frappe
from project_management.utils import *


def get_managed_projects(user):
    project = frappe.qb.DocType("Project")

    return (
        frappe.qb.from_(project)
        .select(project.name)
        .where(project.project_manager == user)
    )


def get_team_projects(user):
    member = frappe.qb.DocType("Project Team Member")

    return (
        frappe.qb.from_(member)
        .select(member.parent)
        .where(
            (member.user == user)
            & (member.parenttype == "Project")
            & (member.parentfield == "project_team_members")
        )
    )


def get_vendor_projects(user):
    member = frappe.qb.DocType("Project Vendor Member")

    return (
        frappe.qb.from_(member)
        .select(member.parent)
        .where(
            (member.user == user)
            & (member.parenttype == "Project")
            & (member.parentfield == "project_vendor_members")
        )
    )


def is_project_vendor_member(project_name, user):
    return frappe.db.exists(
        "Project Vendor Member",
        {
            "parent": project_name,
            "parenttype": "Project",
            "parentfield": "project_vendor_members",
            "user": user
        }
    )


def combine_conditions(conditions, fallback_condition, table_name=None):
    if not conditions:
        final_condition = fallback_condition.get_sql()
    else:
        final_condition = conditions[0]

        for condition in conditions[1:]:
            final_condition = final_condition | condition

        final_condition = final_condition.get_sql()
    if table_name:
        final_condition = final_condition.replace(
            "project IN",
            f"`{table_name}`.`project` IN"
        )

    return final_condition


def has_project_permission(doc, user=None, ptype=None, debug=False):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return True

    roles = get_user_roles(user)

    if "Project Manager" in roles:
        if doc.project_manager == user:
            return True

    if "Project Team Member" in roles:
        if is_project_team_member(doc.name, user):
            return True

    return False


def get_project_permission_query(user=None):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return ""

    roles = get_user_roles(user)

    conditions = []

    if "Project Manager" in roles:
        conditions.append(
            "`tabProject`.`project_manager` = " + frappe.db.escape(user)
        )

    if "Project Team Member" in roles:
        conditions.append(
            """
            `tabProject`.`name` IN (
                SELECT `parent`
                FROM `tabProject Team Member`
                WHERE `user` = {0}
                AND `parenttype` = 'Project'
                AND `parentfield` = 'project_team_members'
            )
            """.format(frappe.db.escape(user))
        )

    if not conditions:
        return "`tabProject`.`name` = ''"

    return "(" + " OR ".join(conditions) + ")"

def has_task_permission(doc, user=None, ptype=None, debug=False):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return True

    roles = get_user_roles(user)

    if "Project Manager" in roles:
        if doc.project and is_project_manager(doc.project, user):
            return True

    if "Project Team Member" in roles:
        if doc.assigned_to == user:
            if is_project_team_member(doc.project, user):
                return True

    if "Project Vendor" in roles:
        if doc.assigned_to == user:
            if is_project_vendor_member(doc.project, user):
                return True

    return False


def get_task_permission_query(user=None):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return ""

    roles = get_user_roles(user)
    task = frappe.qb.DocType("Task")

    conditions = []

    if "Project Manager" in roles:
        conditions.append(
            task.project.isin(get_managed_projects(user))
        )

    if "Project Team Member" in roles:
        conditions.append(
            (task.assigned_to == user)
            & (task.project.isin(get_team_projects(user)))
        )

    if "Project Vendor" in roles:
        conditions.append(
            (task.assigned_to == user)
            & (task.project.isin(get_vendor_projects(user)))
        )

    return combine_conditions(
        conditions,
        task.name == "",
        "tabTask"
    )

def has_my_day_task_permission(doc, user=None, ptype=None, debug=False):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return True

    roles = get_user_roles(user)

    if "Project Team Member" in roles:
        if doc.user == user:
            return True

    if "Project Manager" in roles:
        project_name = frappe.db.get_value(
            "Task",
            doc.task,
            "project"
        )

        if project_name and is_project_manager(project_name, user):
            return True

    return False


def get_my_day_task_permission_query(user=None):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return ""

    roles = get_user_roles(user)
    my_day = frappe.qb.DocType("My Day Task")

    conditions = []

    if "Project Team Member" in roles:
        conditions.append(my_day.user == user)

    if "Project Manager" in roles:
        task = frappe.qb.DocType("Task")

        managed_tasks = (
            frappe.qb.from_(task)
            .select(task.name)
            .where(task.project.isin(get_managed_projects(user)))
        )

        conditions.append(my_day.task.isin(managed_tasks))

    return combine_conditions(
        conditions,
        my_day.name == ""
    )

def has_time_log_permission(doc, user=None, ptype=None, debug=False):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return True

    roles = get_user_roles(user)

    if "Project Manager" in roles:
        if doc.project and is_project_manager(doc.project, user):
            return True

    if "Project Team Member" in roles:
        if doc.user == user:
            if is_project_team_member(doc.project, user):
                return True

    if "Project Vendor" in roles:
        if doc.user == user:
            if is_project_vendor_member(doc.project, user):
                return True

    return False


def get_time_log_permission_query(user=None):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return ""

    roles = get_user_roles(user)
    time_log = frappe.qb.DocType("Time Log")

    conditions = []

    if "Project Manager" in roles:
        conditions.append(
            time_log.project.isin(get_managed_projects(user))
        )

    if "Project Team Member" in roles:
        conditions.append(
            (time_log.user == user)
            & (time_log.project.isin(get_team_projects(user)))
        )

    if "Project Vendor" in roles:
        conditions.append(
            (time_log.user == user)
            & (time_log.project.isin(get_vendor_projects(user)))
        )

    return combine_conditions(
        conditions,
        time_log.name == "",
        "tabTime Log"
    )

def has_deliverable_permission(doc, user=None, ptype=None, debug=False):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return True

    roles = get_user_roles(user)

    if "Project Manager" in roles:
        if doc.project and is_project_manager(doc.project, user):
            return True

    if "Project Team Member" in roles:
        if is_project_team_member(doc.project, user):
            return True

    if "Project Vendor" in roles:
        if doc.submitted_by == user:
            if is_project_vendor_member(doc.project, user):
                return True

    return False


def get_deliverable_permission_query(user=None):
    if not user:
        user = frappe.session.user

    if is_admin(user):
        return ""

    roles = get_user_roles(user)
    deliverable = frappe.qb.DocType("Deliverable")

    conditions = []

    if "Project Manager" in roles:
        conditions.append(
            deliverable.project.isin(get_managed_projects(user))
        )

    if "Project Team Member" in roles:
        conditions.append(
            deliverable.project.isin(get_team_projects(user))
        )

    if "Project Vendor" in roles:
        conditions.append(
            (deliverable.submitted_by == user)
            & (deliverable.project.isin(get_vendor_projects(user)))
        )

    return combine_conditions(
        conditions,
        deliverable.name == "",
        "tabDeliverable"
    )
