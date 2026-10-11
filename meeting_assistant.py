from llm import client, MODEL_NAME


def create_meeting_agenda(request):

    prompt = f"""
You are an AI Executive Office Assistant.

Create a professional meeting agenda.

Meeting request:
{request}

Include:

1. Meeting objective
2. Topics to discuss
3. Suggested agenda
4. Expected outcomes
5. Required participants

Do not invent specific facts that were not provided.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def summarize_meeting(meeting_notes):

    prompt = f"""
Summarize these meeting notes.

Identify:

1. Meeting summary
2. Key discussion points
3. Decisions made
4. Action items
5. Owners
6. Deadlines

Meeting notes:
{meeting_notes}

Only use information present in the notes.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


def extract_action_items(meeting_notes):

    prompt = f"""
Extract action items from these meeting notes.

For each action item identify:

- Action
- Owner
- Deadline

Meeting notes:
{meeting_notes}

If an owner or deadline is not mentioned,
write "Not specified".

Do not invent information.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content