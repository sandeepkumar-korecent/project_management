
frappe.listview_settings["My Day Task"] = {

    add_fields: ["user", "task", "plan_date"],

    filters: [
        ["user", "=", frappe.session.user],
        ["plan_date", "=", frappe.datetime.get_today()]
    ],
    onload: function(listview) {
        listview.page.add_inner_button(
            __("Add Task to My Day"),
            function() {

                frappe.new_doc("My Day Task", {
                    user: frappe.session.user,
                    plan_date: frappe.datetime.get_today()
                });

            }
        );

    }

};
