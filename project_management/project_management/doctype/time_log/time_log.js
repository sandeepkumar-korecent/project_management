// Copyright (c) 2026, Sandeep Kumar and contributors
// For license information, please see license.txt


frappe.ui.form.on("Time Log", {
    refresh: function(frm) {
        if (frm.is_new()) {
            frm.set_value("user", frappe.session.user);
        }
    },

    task: function(frm) {
        if (!frm.doc.task) {
            frm.set_value("project", "");
            return;
        }
        frappe.db.get_value(
            "Task",
            frm.doc.task,
            ["project", "assigned_to"]
        ).then(function(response) {
            if (response.message) {
                frm.set_value("project", response.message.project);
                frm.set_value("user", response.message.assigned_to);

            }
        });
    },

    start_time: function(frm) {
        frm.trigger("check_time");
    },

    end_time: function(frm) {
        frm.trigger("check_time");
    },

    check_time: function(frm) {

        if (frm.doc.start_time && frm.doc.end_time) {

            let start = moment(frm.doc.start_time);
            let end = moment(frm.doc.end_time);

            if (end.isSameOrBefore(start)) {

                frappe.msgprint(
                    "End Time must be later than Start Time."
                );

                frm.set_value("end_time", "");

            }

        }

    }

});

