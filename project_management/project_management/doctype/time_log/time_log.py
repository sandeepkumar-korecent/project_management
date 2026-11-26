
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime
from project_management.utils import is_admin


class TimeLog(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        description: DF.SmallText | None
        end_time: DF.Datetime | None
        hours: DF.Float
        project: DF.Link
        start_time: DF.Datetime | None
        task: DF.Link
        user: DF.Link
    # end: auto-generated types

    _DOCTYPE_NAME = "Time Log"

    def validate(self):
        self.check_user()
        self.check_task()
        self.check_project()
        self.check_time()
        self.calculate_hours()

    def check_user(self):
        current_user = frappe.session.user

        if not self.user:
            self.user = current_user

        if not frappe.db.exists("User", self.user):
            frappe.throw("Selected User does not exist.")

        if not is_admin(current_user) and self.user != current_user:
            frappe.throw("You can create time logs only for yourself.")

    def check_task(self):
        if not self.task:
            frappe.throw("Please select a Task.")

        if not frappe.db.exists("Task", self.task):
            frappe.throw("Selected Task does not exist.")

        task_user = frappe.db.get_value(
            "Task", self.task, "assigned_to"
        )

        if task_user != self.user:
            frappe.throw("You can log time only for your assigned Tasks.")

    def check_project(self):
        if not self.project:
            frappe.throw("Please select a Project.")

        task_project = frappe.db.get_value(
            "Task", self.task, "project"
        )

        if self.project != task_project:
            frappe.throw(
                "Selected Project does not match the Task Project."
            )

    def check_time(self):
        if self.start_time and not self.end_time:
            frappe.throw("Please enter End Time.")

        if self.end_time and not self.start_time:
            frappe.throw("Please enter Start Time.")

        if self.start_time and self.end_time:
            start_time = get_datetime(self.start_time)
            end_time = get_datetime(self.end_time)

            if end_time <= start_time:
                frappe.throw("End Time must be later than Start Time.")

    def calculate_hours(self):
        if self.start_time and self.end_time:
            start_time = get_datetime(self.start_time)
            end_time = get_datetime(self.end_time)

            time_difference = end_time - start_time
            total_hours = time_difference.total_seconds() / 3600

            self.hours = round(total_hours, 2)

        elif not self.hours or self.hours <= 0:
            frappe.throw("Please enter Hours greater than zero.")
