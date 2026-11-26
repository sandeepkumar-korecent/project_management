
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from project_management.utils import (
    is_admin,
    is_project_manager,
    is_project_team_member
)


class Deliverable(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from project_management.project_management.doctype.deliverable_task.deliverable_task import DeliverableTask

        client_feedback: DF.TextEditor | None
        deliverable_name: DF.Data
        description: DF.TextEditor | None
        file: DF.Attach
        project: DF.Link
        reviewed_by: DF.Link | None
        reviewed_on: DF.Datetime | None
        status: DF.Literal["Submitted", "Changes Requested", "Accepted"]
        submitted_by: DF.Link
        submitted_on: DF.Datetime | None
        tasks: DF.Table[DeliverableTask]
    # end: auto-generated types

    _DOCTYPE_NAME = "Deliverable"

    def validate(self):
        self.check_project()
        self.check_submitted_by()
        self.check_file()
        self.check_tasks()
        self.check_review_permission()
        self.update_submission_details()
        self.update_review_details()

    def check_project(self):
        if not self.project:
            frappe.throw("Please select a Project.")

        if not frappe.db.exists("Project", self.project):
            frappe.throw("Selected Project does not exist.")

    def check_submitted_by(self):
        current_user = frappe.session.user

        if not self.submitted_by:
            self.submitted_by = current_user

        if not frappe.db.exists("User", self.submitted_by):
            frappe.throw("Selected user does not exist.")

        if is_admin(current_user):
            return

        if self.is_new() and self.submitted_by != current_user:
            frappe.throw("You can submit a Deliverable only as yourself.")

        old_doc = self.get_doc_before_save()

        if old_doc and old_doc.submitted_by != self.submitted_by:
            frappe.throw("You cannot change the original submitter.")

        is_manager = is_project_manager(self.project, current_user)
        is_team_member = is_project_team_member(self.project, current_user)

        is_vendor_member = frappe.db.exists(
            "Project Vendor Member",
            {
                "parent": self.project,
                "parenttype": "Project",
                "parentfield": "project_vendor_members",
                "user": current_user
            }
        )

        if not (is_manager or is_team_member or is_vendor_member):
            frappe.throw("You are not a member of this Project.")

    def check_file(self):
        if not self.file:
            frappe.throw("Please attach the Deliverable file.")

    def check_tasks(self):
        task_list = []

        for row in self.tasks:
            if not row.task:
                frappe.throw("Please select a Task.")

            if row.task in task_list:
                frappe.throw("The same Task cannot be added twice.")

            task_list.append(row.task)

            task_project = frappe.db.get_value(
                "Task", row.task, "project"
            )

            if not task_project:
                frappe.throw("Selected Task does not exist.")

            if task_project != self.project:
                frappe.throw(
                    "All linked Tasks must belong to the selected Project."
                )

    def check_review_permission(self):
        current_user = frappe.session.user

        if is_admin(current_user):
            return

        if self.is_new():
            if self.status != "Submitted":
                frappe.throw(
                    "A new Deliverable must have Submitted status."
                )
            return

        old_doc = self.get_doc_before_save()

        if not old_doc:
            return

        is_manager = is_project_manager(self.project, current_user)

        if not is_manager:
            review_fields = [
                "status",
                "client_feedback",
                "reviewed_by",
                "reviewed_on"
            ]

            for field in review_fields:
                if old_doc.get(field) != self.get(field):
                    frappe.throw(
                        "Only the Project Manager can review a Deliverable."
                    )

    def update_submission_details(self):
        if not self.submitted_on:
            self.submitted_on = now_datetime()

    def update_review_details(self):
        current_user = frappe.session.user

        if is_admin(current_user):
            return

        if self.status == "Submitted":
            self.reviewed_by = None
            self.reviewed_on = None

        elif is_project_manager(self.project, current_user):
            self.reviewed_by = current_user
            self.reviewed_on = now_datetime()
