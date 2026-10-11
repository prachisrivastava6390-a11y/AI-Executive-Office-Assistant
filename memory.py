def add_message(
    conversation,
    role,
    content
):

    conversation.append(
        {
            "role": role,
            "content": content
        }
    )

    return conversation


def get_recent_conversation(
    conversation,
    limit=6
):

    recent_messages = conversation[-limit:]

    history = ""

    for message in recent_messages:

        history += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    return history


def clear_memory():

    return []