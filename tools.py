from datetime import datetime
import math

from task_manager import (
    create_task,
    view_tasks,
    complete_task,
    delete_task
)


# =========================================
# CALCULATOR
# =========================================

def calculate(expression):

    try:

        allowed_names = {
            "sqrt": math.sqrt,
            "pow": pow
        }

        result = eval(
            expression,
            {"__builtins__": {}},
            allowed_names
        )

        return f"Calculation result: {result}"

    except Exception:

        return "I could not calculate that expression."


# =========================================
# TIME TOOL
# =========================================

def get_current_time():

    current_time = datetime.now().strftime(
        "%I:%M %p"
    )

    return (
        f"The current local time is "
        f"{current_time}."
    )


# =========================================
# DATE TOOL
# =========================================

def get_current_date():

    current_date = datetime.now().strftime(
        "%d %B %Y"
    )

    return (
        f"Today's date is "
        f"{current_date}."
    )


# =========================================
# TOOL ROUTER
# =========================================

def execute_tool(user_request):

    request = user_request.lower().strip()


    # -----------------------------------------
    # TIME
    # -----------------------------------------

    time_requests = [
        "what time is it",
        "current time",
        "current local time",
        "tell me the time",
        "what is the time"
    ]

    if any(
        phrase in request
        for phrase in time_requests
    ):

        return get_current_time()


    # -----------------------------------------
    # DATE
    # -----------------------------------------

    date_requests = [
        "what is today's date",
        "what is the date",
        "today's date",
        "current date",
        "tell me the date"
    ]

    if any(
        phrase in request
        for phrase in date_requests
    ):

        return get_current_date()


    # -----------------------------------------
    # CALCULATOR
    # -----------------------------------------

    if request.startswith("calculate"):

        expression = request.replace(
            "calculate",
            "",
            1
        ).strip()

        return calculate(expression)


    # -----------------------------------------
    # CREATE TASK
    # -----------------------------------------

    if request.startswith("create task"):

        task_name = request.replace(
            "create task",
            "",
            1
        ).strip()

        if not task_name:

            return "Please provide a task name."

        return create_task(task_name)


    # -----------------------------------------
    # ADD TASK
    # -----------------------------------------

    if request.startswith("add task"):

        task_name = request.replace(
            "add task",
            "",
            1
        ).strip()

        if not task_name:

            return "Please provide a task name."

        return create_task(task_name)


    # -----------------------------------------
    # VIEW TASKS
    # -----------------------------------------

    if (
        "show my tasks" in request
        or "show tasks" in request
        or "view tasks" in request
        or "list tasks" in request
    ):

        return view_tasks()


    # -----------------------------------------
    # COMPLETE TASK
    # -----------------------------------------

    if request.startswith("complete task"):

        task_id = request.replace(
            "complete task",
            "",
            1
        ).strip()

        return complete_task(task_id)


    # -----------------------------------------
    # DELETE TASK
    # -----------------------------------------

    if request.startswith("delete task"):

        task_id = request.replace(
            "delete task",
            "",
            1
        ).strip()

        return delete_task(task_id)


    # -----------------------------------------
    # NO TOOL MATCH
    # -----------------------------------------

    return None