
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from project_management.utils import is_admin


class MyDayTask(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        display_order: DF.Int
        plan_date: DF.Date
        task: DF.Link
        user: DF.Link
    # end: auto-generated types

    _DOCTYPE_NAME = "My Day Task"

    def validate(self):
        self.check_user()
        self.check_task()
        self.check_plan_date()
        self.check_duplicate_task()

    def check_user(self):
        current_user = frappe.session.user

        if not self.user:
            self.user = current_user

        if not frappe.db.exists("User", self.user):
            frappe.throw("Selected User does not exist.")

        if not is_admin(current_user) and self.user != current_user:
            frappe.throw("You can manage My Day tasks only for yourself.")

    def check_task(self):
        if not self.task:
            frappe.throw("Please select a Task.")

        task = frappe.get_doc("Task", self.task)

        if task.assigned_to != self.user:
            frappe.throw("You can add only tasks assigned to yourself.")

    def check_plan_date(self):
        if not self.plan_date:
            frappe.throw("Please select a Plan Date.")

    def check_duplicate_task(self):
        existing_task = frappe.db.exists(
            "My Day Task",
            {
                "user": self.user,
                "task": self.task,
                "plan_date": self.plan_date,
                "name": ["!=", self.name]
            }
        )

        if existing_task:
            frappe.throw(
                "This Task is already added to My Day for this date."
            )
