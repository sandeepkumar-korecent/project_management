
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days


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
            "width": 160
        },
        {
            "label": _("Task"),
            "fieldname": "task",
            "fieldtype": "Link",
            "options": "Task",
            "width": 160
        },
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "Link",
            "options": "User",
            "width": 160
        },
        {
            "label": _("Start Time"),
            "fieldname": "start_time",
            "fieldtype": "Datetime",
            "width": 170
        },
        {
            "label": _("End Time"),
            "fieldname": "end_time",
            "fieldtype": "Datetime",
            "width": 170
        },
        {
            "label": _("Hours"),
            "fieldname": "hours",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Description"),
            "fieldname": "description",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    return columns


def get_data(filters):
    conditions = []

    if filters.get("project"):
        conditions.append(
            ["project", "=", filters.get("project")]
        )

    if filters.get("user"):
        conditions.append(
            ["user", "=", filters.get("user")]
        )

    if filters.get("from_date"):
        conditions.append(
            ["start_time", ">=", filters.get("from_date")]
        )

    if filters.get("to_date"):
        conditions.append(
            ["start_time", "<", add_days(filters.get("to_date"), 1)]
        )

    data = frappe.get_list(
        "Time Log",
        fields=[
            "project",
            "task",
            "user",
            "start_time",
            "end_time",
            "hours",
            "description"
        ],
        filters=conditions,
        order_by="start_time desc",
        page_length=1000
    )

    return data
