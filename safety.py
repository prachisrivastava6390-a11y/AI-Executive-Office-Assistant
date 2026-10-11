# =========================================
# SAFETY CHECK
# =========================================

def requires_confirmation(action):

    confirmation_actions = [
        "send email",
        "delete task",
        "delete document",
        "create meeting",
        "schedule meeting",
        "modify calendar"
    ]

    action_lower = action.lower()

    for item in confirmation_actions:

        if item in action_lower:
            return True

    return False


# =========================================
# CONFIRMATION MESSAGE
# =========================================

def confirmation_message(action):

    return (
        f"This action may make a real change: {action}\n\n"
        "Please confirm before continuing."
    )


# =========================================
# CHECK USER CONFIRMATION
# =========================================

def is_confirmed(user_response):

    response = user_response.lower().strip()

    confirmation_words = [
        "yes",
        "confirm",
        "confirmed",
        "proceed",
        "do it",
        "go ahead"
    ]

    return any(
        word in response
        for word in confirmation_words
    )