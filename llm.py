from dotenv import load_dotenv
import os

from groq import Groq


# =========================================
# LOAD ENVIRONMENT
# =========================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "openai/gpt-oss-120b"


# =========================================
# GENERAL AI RESPONSE
# =========================================

def generate_response(
    user_request,
    context="",
    conversation_history=""
):

    prompt = f"""
You are an AI Executive Office Assistant
for Prachiva Office Solutions Pvt. Ltd.

Your job is to help employees with:

- Company information
- Company policies
- Office tasks
- Uploaded documents
- Summaries
- Key points
- Important decisions
- General office questions

Company Information:
{context}

Previous Conversation:
{conversation_history}

User Request:
{user_request}


Instructions:

- Answer clearly and professionally.
- Use the provided company information when relevant.
- Use previous conversation context when useful.
- Do not invent company policies.
- If company information is unavailable,
  clearly say that it is not available in
  the company knowledge base.
- Keep answers easy to understand.
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


# =========================================
# DOCUMENT SUMMARIZATION
# =========================================

def summarize_text(document_text):

    prompt = f"""
You are an AI document summarization assistant.

Summarize the following document.

DOCUMENT:
{document_text}


Provide:

1. Short Summary
2. Key Points
3. Important Decisions
4. Important Dates
5. Action Items


Rules:

- Do not invent information.
- Only use information present
  in the document.
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


# =========================================
# EXTRACT KEY POINTS
# =========================================

def extract_key_points(document_text):

    prompt = f"""
Extract the most important information
from the following document.

DOCUMENT:
{document_text}


Return:

- Key Points
- Important Decisions
- Action Items
- Important Dates


Rules:

- Only use information present
  in the document.
- Do not invent information.
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

