
// Copyright (c) 2026, Sandeep Kumar and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Report"] = {
    filters: [
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project"
        },
        {
            fieldname: "client",
            label: __("Client"),
            fieldtype: "Link",
            options: "Client"
        },
        {
            fieldname: "project_manager",
            label: __("Project Manager"),
            fieldtype: "Link",
            options: "User"
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nPlanning\nIn Progress\nOn Hold\nCompleted"
        }
    ]
};
