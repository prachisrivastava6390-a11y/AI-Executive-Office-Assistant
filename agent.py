from llm import (
    generate_response,
    summarize_text,
    extract_key_points
)

from rag import (
    search_knowledge_base,
    search_document
)

from tools import execute_tool

from email_assistant import (
    draft_email,
    improve_email,
    summarize_email
)

from meeting_assistant import (
    create_meeting_agenda,
    summarize_meeting,
    extract_action_items
)

from task_manager import (
    create_task,
    view_tasks,
    complete_task,
    delete_task
)

from safety import (
    requires_confirmation,
    confirmation_message
)


def process_request(
    user_request,
    document_text=None,
    conversation_history=""
):

    request = user_request.lower().strip()

    # --------------------------------
    # 1. SAFETY
    # --------------------------------
    if requires_confirmation(request):
        return confirmation_message(user_request)

    # --------------------------------
    # 2. TOOLS
    # --------------------------------
    tool_result = execute_tool(user_request)

    if tool_result:
        return tool_result

    # --------------------------------
    # 3. EMAIL ASSISTANT
    # --------------------------------

    if (
        "draft email" in request
        or "write an email" in request
        or "compose email" in request
        or "create email" in request
    ):
        return draft_email(user_request)

    if (
        "improve email" in request
        or "rewrite email" in request
        or "rewrite this email" in request
    ):
        return improve_email(user_request)

    if (
        "summarize email" in request
        or "summarize this email" in request
        or "summarize the email" in request
        or "summary of this email" in request
        or "summarise email" in request
        or "summarise this email" in request
    ):
        return summarize_email(user_request)

    # --------------------------------
    # 4. MEETING ASSISTANT
    # --------------------------------

    if (
        "create meeting agenda" in request
        or "meeting agenda" in request
        or "prepare meeting agenda" in request
    ):
        return create_meeting_agenda(user_request)

    if (
        "summarize meeting" in request
        or "meeting summary" in request
        or "summarize meeting notes" in request
    ):
        if document_text:
            return summarize_meeting(document_text)

        return summarize_meeting(user_request)

    # ACTION ITEMS
    if (
        "action items" in request
        or "extract action items" in request
    ):

        # If the user explicitly provides meeting notes
        # in the current request, use those notes.
        if (
            "meeting notes" in request
            or "these notes" in request
            or "following notes" in request
        ):
            return extract_action_items(user_request)

        # Otherwise use the uploaded document
        if document_text:
            return extract_action_items(document_text)

        # If no document is uploaded,
        # use the user's request.
        return extract_action_items(user_request)

    # --------------------------------
    # 5. TASK MANAGEMENT
    # --------------------------------

    if request.startswith("create task"):

        task_name = request.replace(
            "create task",
            "",
            1
        ).strip()

        if not task_name:
            return "Please provide a task name."

        return create_task(task_name)

    if request.startswith("add task"):

        task_name = request.replace(
            "add task",
            "",
            1
        ).strip()

        if not task_name:
            return "Please provide a task name."

        return create_task(task_name)

    if (
        "show tasks" in request
        or "view tasks" in request
        or "list tasks" in request
        or "show my tasks" in request
    ):
        return view_tasks()

    if request.startswith("complete task"):

        task_id = request.replace(
            "complete task",
            "",
            1
        ).strip()

        return complete_task(task_id)

    if request.startswith("delete task"):

        task_id = request.replace(
            "delete task",
            "",
            1
        ).strip()

        return delete_task(task_id)

    # --------------------------------
    # 6. DOCUMENT INTELLIGENCE
    # --------------------------------

    if document_text:

        if (
            "summarize this document" in request
            or "summarise this document" in request
            or "summarize the document" in request
            or "summary of this document" in request
        ):
            return summarize_text(document_text)

        if (
            "key points" in request
            or "important points" in request
            or "important decisions" in request
        ):
            return extract_key_points(document_text)

        context = search_document(
            document_text,
            user_request
        )

        return generate_response(
            user_request,
            context,
            conversation_history
        )

    # --------------------------------
    # 7. COMPANY KNOWLEDGE RAG
    # --------------------------------

    context = search_knowledge_base(
        user_request
    )

    # --------------------------------
    # 8. GENERAL LLM
    # --------------------------------

    return generate_response(
        user_request,
        context,
        conversation_history
    )