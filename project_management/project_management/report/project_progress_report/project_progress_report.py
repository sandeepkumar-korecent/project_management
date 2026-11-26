
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 170
        },
        {
            "label": _("Client"),
            "fieldname": "client",
            "fieldtype": "Link",
            "options": "Client",
            "width": 150
        },
        {
            "label": _("Project Manager"),
            "fieldname": "project_manager",
            "fieldtype": "Link",
            "options": "User",
            "width": 160
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Total Tasks"),
            "fieldname": "total_tasks",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Completed Tasks"),
            "fieldname": "completed_tasks",
            "fieldtype": "Int",
            "width": 130
        },
        {
            "label": _("Pending Tasks"),
            "fieldname": "pending_tasks",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Overall Progress"),
            "fieldname": "overall_progress",
            "fieldtype": "Percent",
            "width": 140
        },
        {
            "label": _("Start Date"),
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": _("End Date"),
            "fieldname": "end_date",
            "fieldtype": "Date",
            "width": 110
        }
    ]

    return columns


def get_data(filters):
    conditions = []

    if filters.get("project"):
        conditions.append(
            ["name", "=", filters.get("project")]
        )

    if filters.get("client"):
        conditions.append(
            ["client", "=", filters.get("client")]
        )

    if filters.get("project_manager"):
        conditions.append(
            ["project_manager", "=", filters.get("project_manager")]
        )

    if filters.get("status"):
        conditions.append(
            ["status", "=", filters.get("status")]
        )

    projects = frappe.get_list(
        "Project",
        fields=[
            "name",
            "client",
            "project_manager",
            "status",
            "start_date",
            "end_date"
        ],
        filters=conditions,
        order_by="modified desc",
        page_length=1000
    )

    project_names = []

    for project in projects:
        project_names.append(project.name)

    if not project_names:
        return []

    tasks = frappe.get_list(
        "Task",
        fields=[
            "project",
            "status",
            "progress"
        ],
        filters={
            "project": ["in", project_names]
        },
        page_length=10000
    )

    project_summary = {}

    for project in projects:
        project_summary[project.name] = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "progress_sum": 0
        }

    for task in tasks:
        if task.project in project_summary:
            project_summary[task.project]["total_tasks"] += 1

            if task.status == "Completed":
                project_summary[task.project]["completed_tasks"] += 1

            project_summary[task.project]["progress_sum"] += task.progress or 0

    data = []

    for project in projects:
        summary = project_summary[project.name]

        total_tasks = summary["total_tasks"]
        completed_tasks = summary["completed_tasks"]

        pending_tasks = total_tasks - completed_tasks

        overall_progress = 0

        if total_tasks > 0:
            overall_progress = round(
                summary["progress_sum"] / total_tasks,
                2
            )

        data.append({
            "project": project.name,
            "client": project.client,
            "project_manager": project.project_manager,
            "status": project.status,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "overall_progress": overall_progress,
            "start_date": project.start_date,
            "end_date": project.end_date
        })

    return data
