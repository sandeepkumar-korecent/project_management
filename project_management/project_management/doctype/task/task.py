
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime
from project_management.utils import (
    is_admin,
    is_project_manager,
    is_project_team_member
)

class Task(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assigned_to: DF.Link
		completed_on: DF.Datetime | None
		description: DF.TextEditor | None
		due_date: DF.Date | None
		progress: DF.Percent
		project: DF.Link
		start_date: DF.Date | None
		status: DF.Literal["Open", "In Progress", "Blocked", "Completed"]
		task_title: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Task"

	def validate(self):
		self.check_task_edit_permission()
		self.check_project()
		self.check_assigned_user()
		self.check_dates()
		self.check_progress()
		self.check_completed_task()

	def check_project(self):
		if not self.project:
			frappe.throw("Please select a Project.")
		if not frappe.db.exists("Project", self.project):
			frappe.throw("Selected Project does not exist.")

	def check_assigned_user(self):
		if not self.assigned_to:
			return
		project = frappe.get_doc("Project", self.project)
		allowed_users = []
		allowed_users.append(project.project_manager)
		for member in project.project_team_members:
			allowed_users.append(member.user)
		for member in project.project_vendor_members:
			allowed_users.append(member.user)

		if self.assigned_to not in allowed_users:
			frappe.throw(
				"Please assign this task to a Project Manager, "
				"team member or vendor member of this project."
			)

	def check_dates(self):
		if self.start_date and self.due_date:
			start_date = getdate(self.start_date)
			due_date = getdate(self.due_date)
			if due_date < start_date:
				frappe.throw("Due Date cannot be earlier than Start Date.")

	def check_progress(self):
		print(f"Progress: {self.progress}")
		print(f"Type of Progress: {type(self.progress)}")
		self.progress = self.progress or 0
		if isinstance(self.progress, str):
			try:
				self.progress = float(self.progress)
			except ValueError:
				frappe.throw("Progress must be a number between 0 and 100.")
		if self.progress is None:
			self.progress = 0
		if self.progress < 0 or self.progress > 100:
			frappe.throw("Progress must be between 0 and 100.")

	def check_completed_task(self):
		if self.status == "Completed":
			self.progress = 100
			if not self.completed_on:
				self.completed_on = now_datetime()
		else:
			self.completed_on = None

	def check_task_edit_permission(self):
		current_user = frappe.session.user
		if is_admin(current_user):
			return
		if self.is_new():
			if not is_project_manager(self.project, current_user):
				frappe.throw("Only the Project Manager can create Tasks.")
			return

		old_doc = self.get_doc_before_save()

		if not old_doc:
			return

		if is_project_manager(old_doc.project, current_user):
			return

		if not is_project_team_member(old_doc.project, current_user):
			frappe.throw("You are not a member of this Project.")

		if old_doc.assigned_to != current_user:
			frappe.throw("You can update only your assigned Tasks.")

		if self.project != old_doc.project:
			frappe.throw("You cannot change the Project of a Task.")

		if self.assigned_to != old_doc.assigned_to:
			frappe.throw("You cannot reassign a Task.")
