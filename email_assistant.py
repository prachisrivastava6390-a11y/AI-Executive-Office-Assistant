from llm import client, MODEL_NAME


def draft_email(request):

    prompt = f"""
You are an AI Executive Office Assistant.

Create a professional business email based on the user's request.

User request:
{request}

Return:
Subject:
Email:

Keep the email professional, clear and concise.
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


def improve_email(email_text):

    prompt = f"""
Improve the following email.

Make it:
- Professional
- Clear
- Polite
- Concise
- Grammatically correct

Email:
{email_text}

Return only the improved email.
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


def summarize_email(email_text):

    prompt = f"""
Summarize the following email.

Identify:
1. Main purpose
2. Key points
3. Action items
4. Deadlines
5. People involved

Email:
{email_text}

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