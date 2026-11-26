# Copyright (c) 2026, Sandeep Kumar and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Client(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		contact_email: DF.Data | None
		contact_name: DF.Data | None
		organization_name: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Client"
