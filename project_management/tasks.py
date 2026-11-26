
import frappe
from frappe.utils import nowdate, add_days


def send_task_reminders():
    today = nowdate()

    projects = frappe.get_all(
        "Project",
        fields=[
            "name",
            "enable_reminders",
            "remind_before_due_days",
            "remind_overdue_tasks"
        ],
        filters={
            "enable_reminders": 1
        },
        page_length=1000
    )

    for project in projects:

        reminder_days = project.remind_before_due_days or 0

        if reminder_days > 0:
            reminder_date = add_days(today, reminder_days)

            upcoming_tasks = frappe.get_all(
                "Task",
                fields=[
                    "name",
                    "task_title",
                    "assigned_to",
                    "due_date"
                ],
                filters=[
                    ["project", "=", project.name],
                    ["status", "!=", "Completed"],
                    ["due_date", "=", reminder_date]
                ],
                page_length=1000
            )

            for task in upcoming_tasks:
                send_reminder_email(
                    task,
                    "Task Due Soon",
                    "Your task is approaching its due date."
                )

        if project.remind_overdue_tasks:
            overdue_tasks = frappe.get_all(
                "Task",
                fields=[
                    "name",
                    "task_title",
                    "assigned_to",
                    "due_date"
                ],
                filters=[
                    ["project", "=", project.name],
                    ["status", "!=", "Completed"],
                    ["due_date", "<", today]
                ],
                page_length=1000
            )

            for task in overdue_tasks:
                send_reminder_email(
                    task,
                    "Overdue Task Reminder",
                    "Your task is overdue. Please update its status."
                )


def send_reminder_email(task, subject, message):

    if not task.assigned_to:
        return

    email = frappe.get_value(
        "User",
        task.assigned_to,
        "email"
    )

    if not email:
        return

    email_message = """
        <p>Hello,</p>
        <p>{0}</p>
        <p><b>Task:</b> {1}</p>
        <p><b>Due Date:</b> {2}</p>
        <p>Please open the Project Management application
        and update your task.</p>
    """.format(
        message,
        task.task_title,
        task.due_date
    )

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=email_message
    )
