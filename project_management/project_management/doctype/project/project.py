
# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate
from frappe.model.document import Document


class Project(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from project_management.project_management.doctype.project_client_member.project_client_member import ProjectClientMember
		from project_management.project_management.doctype.project_team_member.project_team_member import ProjectTeamMember
		from project_management.project_management.doctype.project_vendor_member.project_vendor_member import ProjectVendorMember

		client: DF.Link
		description: DF.TextEditor | None
		enable_reminders: DF.Check
		end_date: DF.Date | None
		project_client_members: DF.Table[ProjectClientMember]
		project_manager: DF.Link
		project_name: DF.Data
		project_team_members: DF.Table[ProjectTeamMember]
		project_vendor_members: DF.Table[ProjectVendorMember]
		remind_before_due_days: DF.Int
		remind_overdue_tasks: DF.Check
		start_date: DF.Date | None
		status: DF.Literal["Planning", "In Progress", "On Hold", "Completed"]
	# end: auto-generated types

	_DOCTYPE_NAME = "Project"

	def validate(self):
		self.validate_project_dates()
		self.validate_team_members()
		self.validate_client_members()
		self.validate_vendor_members()


	def validate_project_dates(self):
		if self.start_date and self.end_date:
			if getdate(self.end_date) < getdate(self.start_date):
				frappe.throw("End Date cannot be earlier than Start Date.")

	def validate_team_members(self):
		team_users = []
		for member in self.project_team_members:
			if member.user in team_users:
				frappe.throw("An employee cannot be added twice to the project team.")
			team_users.append(member.user)
			if member.user == self.project_manager:
				frappe.throw("Project Manager is already selected. Do not add the same person to the team.")

	def validate_client_members(self):
		client_users = []
		for member in self.project_client_members:
			if member.client != self.client:
				frappe.throw("Client member must belong to the selected Project Client.")
			if member.user in client_users:
				frappe.throw("The same client member cannot be added twice.")
			client_users.append(member.user)

	def validate_vendor_members(self):
		vendor_members = []
		for member in self.project_vendor_members:
			member_name = member.user + "-" + member.vendor
			if member_name in vendor_members:
				frappe.throw("The same vendor member cannot be added twice for the same vendor.")
			vendor_members.append(member_name)
