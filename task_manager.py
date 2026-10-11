from datetime import datetime


tasks = []


# =========================================
# CREATE TASK
# =========================================

def create_task(task_name, priority="Medium"):

    task = {
        "id": len(tasks) + 1,
        "task": task_name,
        "priority": priority,
        "status": "Pending",
        "created_at": datetime.now().strftime(
            "%d %B %Y %I:%M %p"
        )
    }

    tasks.append(task)

    return (
        f"Task created successfully: "
        f"{task_name} "
        f"(Priority: {priority})"
    )


# =========================================
# VIEW TASKS
# =========================================

def view_tasks():

    if not tasks:
        return "There are currently no tasks."

    result = "Office Tasks:\n\n"

    for task in tasks:

        result += (
            f"{task['id']}. "
            f"{task['task']} | "
            f"Priority: {task['priority']} | "
            f"Status: {task['status']}\n"
        )

    return result


# =========================================
# COMPLETE TASK
# =========================================

def complete_task(task_id):

    try:

        task_id = int(task_id)

        for task in tasks:

            if task["id"] == task_id:

                task["status"] = "Completed"

                return (
                    f"Task {task_id} "
                    f"marked as completed."
                )

        return (
            f"Task {task_id} was not found."
        )

    except ValueError:

        return "Please provide a valid task number."


# =========================================
# DELETE TASK
# =========================================

def delete_task(task_id):

    try:

        task_id = int(task_id)

        for task in tasks:

            if task["id"] == task_id:

                tasks.remove(task)

                return (
                    f"Task {task_id} "
                    f"deleted successfully."
                )

        return (
            f"Task {task_id} was not found."
        )

    except ValueError:

        return "Please provide a valid task number."