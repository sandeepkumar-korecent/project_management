
// Copyright (c) 2026, Sandeep Kumar and contributors
// For license information, please see license.txt

frappe.query_reports["Time Tracking Report"] = {
    filters: [
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project"
        },
        {
            fieldname: "user",
            label: __("User"),
            fieldtype: "Link",
            options: "User"
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date"
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date"
        }
    ]
};
