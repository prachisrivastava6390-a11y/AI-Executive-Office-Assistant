import ast
import math
import operator as op
from datetime import datetime
 
from task_manager import (
    create_task,
    view_tasks,
    complete_task,
    delete_task
)
 
 
# =========================================
# CALCULATOR (safe AST-based, no eval)
# =========================================
 
MAX_EXPR_LENGTH = 200
MAX_EXPONENT = 100
 
_BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}
 
_UNARY_OPS = {
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}
 
 
def _safe_pow(base, exponent):
 
    if abs(exponent) > MAX_EXPONENT:
 
        raise ValueError("Exponent too large")
 
    return pow(base, exponent)
 
 
# sqrt aur pow pehle ki tarah allowed hain
_FUNCS = {
    "sqrt": math.sqrt,
    "pow": _safe_pow,
}
 
 
def safe_calculate(expression):
 
    if len(expression) > MAX_EXPR_LENGTH:
 
        raise ValueError("Expression too long")
 
    def _eval(node):
 
        if isinstance(node, ast.Expression):
 
            return _eval(node.body)
 
        if isinstance(node, ast.Constant):
 
            if (
                isinstance(node.value, (int, float))
                and not isinstance(node.value, bool)
            ):
 
                return node.value
 
            raise ValueError("Only numbers allowed")
 
        if (
            isinstance(node, ast.BinOp)
            and type(node.op) in _BIN_OPS
        ):
 
            left = _eval(node.left)
            right = _eval(node.right)
 
            if isinstance(node.op, ast.Pow):
 
                return _safe_pow(left, right)
 
            return _BIN_OPS[type(node.op)](left, right)
 
        if (
            isinstance(node, ast.UnaryOp)
            and type(node.op) in _UNARY_OPS
        ):
 
            return _UNARY_OPS[type(node.op)](
                _eval(node.operand)
            )
 
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS
            and not node.keywords
        ):
 
            args = [_eval(a) for a in node.args]
 
            return _FUNCS[node.func.id](*args)
 
        raise ValueError("Unsupported expression")
 
    return _eval(
        ast.parse(expression.strip(), mode="eval")
    )
 
 
def calculate(expression):
 
    try:
 
        result = safe_calculate(expression)
 
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