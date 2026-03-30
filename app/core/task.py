from datetime import datetime

def update_task_status_if_overdue(task):
    if (
        task.due_date and
        datetime.utcnow() > task.due_date and
        task.status != "completed"
    ):
        task.status = "overdue"