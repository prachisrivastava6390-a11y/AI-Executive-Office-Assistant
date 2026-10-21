import ast
import math
import operator
import streamlit as st

from datetime import datetime
from zoneinfo import ZoneInfo

from task_manager import tasks
from agent import process_request
from rag import extract_document_text
from memory import add_message, get_recent_conversation


# =========================================
# PAGE CONFIGURATION
# =========================================

st.set_page_config(
    page_title="AI Executive Office Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================
# CUSTOM CSS
# =========================================

st.markdown(
    """
    <style>
    .main {
        padding-top: 1rem;
    }

    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    .document-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 1rem;
    }

    .document-name {
        font-weight: 600;
        font-size: 1rem;
        word-break: break-word;
    }

    .document-type {
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    .chat-header {
        font-size: 1.25rem;
        font-weight: 650;
        margin-bottom: 0.5rem;
    }

    .section-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .footer-text {
        text-align: center;
        color: #888888;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================
# SESSION STATE
# =========================================

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "calculator_open" not in st.session_state:
    st.session_state.calculator_open = False

if "document_text" not in st.session_state:
    st.session_state.document_text = None

if "document_name" not in st.session_state:
    st.session_state.document_name = None

if "document_type" not in st.session_state:
    st.session_state.document_type = None


# =========================================
# INDIA DATE AND TIME
# =========================================

def get_india_time():
    """Return the current date and time in India."""
    return datetime.now(ZoneInfo("Asia/Kolkata"))


# =========================================
# DOCUMENT TYPE DETECTION
# =========================================

def detect_document_type(document_text, document_name=""):

    text = document_text.lower() if document_text else ""
    filename = document_name.lower() if document_name else ""

    cv_keywords = [
        "resume", "curriculum vitae", "professional summary",
        "work experience", "experience", "education", "skills",
        "technical skills", "employment history", "career objective",
        "career summary", "professional experience", "projects",
        "certifications", "linkedin", "objective"
    ]

    cv_filename_keywords = [
        "resume", "cv", "curriculum", "profile"
    ]

    cv_score = sum(keyword in text for keyword in cv_keywords)
    cv_filename_score = sum(
        keyword in filename for keyword in cv_filename_keywords
    )

    meeting_keywords = [
        "meeting", "meeting notes", "agenda", "attendees",
        "participant", "action items", "discussion", "decisions",
        "decision", "minutes of meeting", "minutes", "mom",
        "next steps", "follow up", "follow-up"
    ]

    meeting_filename_keywords = [
        "meeting", "minutes", "mom", "agenda"
    ]

    meeting_score = sum(
        keyword in text for keyword in meeting_keywords
    )
    meeting_filename_score = sum(
        keyword in filename for keyword in meeting_filename_keywords
    )

    policy_keywords = [
        "policy", "company policy", "leave policy",
        "attendance policy", "work from home", "code of conduct",
        "employee policy", "guidelines", "procedure",
        "eligibility", "compliance", "rules and regulations"
    ]

    policy_filename_keywords = [
        "policy", "guideline", "procedure", "rules"
    ]

    policy_score = sum(
        keyword in text for keyword in policy_keywords
    )
    policy_filename_score = sum(
        keyword in filename for keyword in policy_filename_keywords
    )

    scores = {
        "CV / Resume": cv_score + cv_filename_score * 3,
        "Meeting Notes": meeting_score + meeting_filename_score * 3,
        "Company Policy": policy_score + policy_filename_score * 3
    }

    detected_type = max(scores, key=scores.get)

    if scores[detected_type] < 2:
        return "General Document"

    return detected_type


# =========================================
# SAFE CALCULATOR
# =========================================

def safe_calculate(expression):
    """
    Calculate arithmetic expressions safely.

    Allowed:
    +, -, *, /, %, **, parentheses and decimal numbers.

    Letters, names, function calls and Python code are rejected.
    """

    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Please enter a calculation.")

    expression = expression.strip()

    if len(expression) > 100:
        raise ValueError("The calculation is too long.")

    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError, MemoryError):
        raise ValueError(
            "Invalid expression. Enter numbers and arithmetic operators only."
        )

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def calculate(node):

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("Only numbers are allowed.")

            if abs(node.value) > 1e100:
                raise ValueError("The number is too large.")

            if isinstance(node.value, float) and not math.isfinite(node.value):
                raise ValueError("Invalid number.")

            return node.value

        if isinstance(node, ast.BinOp):

            operation = allowed_operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported mathematical operation.")

            left = calculate(node.left)
            right = calculate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("The exponent must be between -10 and 10.")

            result = operation(left, right)

            if type(result) not in (int, float):
                raise ValueError("Invalid result.")

            if abs(result) > 1e100:
                raise ValueError("The result is too large.")

            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("The result is too large.")

            return result

        if isinstance(node, ast.UnaryOp):

            operation = allowed_operators.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operation.")

            return operation(calculate(node.operand))

        # Reject variable names, function calls and all other syntax.
        raise ValueError(
            "Letters and unsupported expressions are not allowed."
        )

    try:
        return calculate(tree.body)
    except (ZeroDivisionError, OverflowError, TypeError, ArithmeticError):
        raise ValueError(
            "Unable to calculate. Check your mathematical expression."
        )


# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.title("🤖 Assistant")
    st.caption("AI Executive Office Assistant")
    st.divider()
    st.subheader("✨ Features")

    features = [
        "Company RAG",
        "Document Intelligence",
        "Email Assistant",
        "Meeting Assistant",
        "Task Management",
        "Tools",
        "Conversation Memory",
        "Safety Layer"
    ]

    for feature in features:
        st.write(f"✅ {feature}")

    st.divider()
    st.subheader("💬 Conversation")

    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.conversation = []
        st.rerun()

    st.divider()
    st.caption(
        "Built with RAG + LLM + Agent Orchestration + Tools"
    )


# =========================================
# MAIN HEADER
# =========================================

st.markdown(
    '<div class="app-title">🤖 AI Executive Office Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">'
    "Your AI-powered assistant for office information, documents, "
    "emails, meetings, tasks, and everyday work."
    "</div>",
    unsafe_allow_html=True
)


# =========================================
# DASHBOARD OVERVIEW
# =========================================

st.markdown("## 📊 Office Dashboard")
st.caption("Your AI-powered workspace at a glance")

total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks
    if task["status"] == "Completed"
)

pending_tasks = sum(
    1 for task in tasks
    if task["status"] == "Pending"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Total Tasks", total_tasks)

with col2:
    st.metric("⏳ Pending Tasks", pending_tasks)

with col3:
    st.metric("✅ Completed Tasks", completed_tasks)

with col4:
    st.metric(
        "💬 Messages",
        len(st.session_state.conversation)
    )


# =========================================
# QUICK ACTIONS
# =========================================

st.markdown(
    '<div class="section-label">Quick Actions</div>',
    unsafe_allow_html=True
)

st.write("")

quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

quick_request = None

with quick_col1:
    if st.button("🕐 Check Time", use_container_width=True):
        quick_request = "What is the current time in India?"

with quick_col2:
    if st.button("📅 Check Date", use_container_width=True):
        quick_request = "What is today's date in India?"

with quick_col3:
    if st.button("🏢 Company Policies", use_container_width=True):
        quick_request = "What are the company policies?"

with quick_col4:
    if st.button("🧮 Calculator", use_container_width=True):
        st.session_state.calculator_open = (
            not st.session_state.calculator_open
        )


# =========================================
# CALCULATOR PANEL
# =========================================

if st.session_state.calculator_open:

    st.markdown("### 🧮 Calculator")
    st.caption(
        "Use numbers, parentheses and arithmetic operators. "
        "Letters and code are not accepted."
    )

    with st.form("calculator_form"):

        calculator_expression = st.text_input(
            "Enter calculation",
            placeholder="Example: (76 * 9) / 2",
            key="calculator_expression"
        )

        calculate_clicked = st.form_submit_button(
            "Calculate",
            use_container_width=True
        )

    if calculate_clicked:
        try:
            result = safe_calculate(calculator_expression)
            st.success(f"Result: {result}")
        except ValueError as error:
            st.error(str(error))


# =========================================
# MAIN WORKSPACE
# =========================================

chat_col, document_col = st.columns([2.2, 1], gap="large")


# =========================================
# CHAT AREA
# =========================================

with chat_col:

    st.markdown(
        '<div class="chat-header">💬 Assistant Conversation</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Ask questions, give instructions, or work with your uploaded document."
    )

    if st.session_state.conversation:

        for message in st.session_state.conversation:

            with st.chat_message(message["role"]):
                st.write(message["content"])

    else:
        st.info("👋 Start a conversation by asking me something below.")

    user_request = st.chat_input("Ask your assistant...")


# =========================================
# DOCUMENT AREA
# =========================================

with document_col:

    st.markdown(
        '<div class="chat-header">📄 Documents</div>',
        unsafe_allow_html=True
    )

    st.caption("Upload a PDF, DOCX, or TXT file for analysis.")

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:

        if st.session_state.document_name != uploaded_file.name:

            try:
                document_text = extract_document_text(uploaded_file)

                st.session_state.document_text = document_text
                st.session_state.document_name = uploaded_file.name

                st.session_state.document_type = detect_document_type(
                    document_text,
                    uploaded_file.name
                )

            except Exception as error:
                st.error(f"Could not process the document: {error}")

    if st.session_state.document_name:

        st.markdown(
            f"""
            <div class="document-card">
                <div class="document-name">
                    📄 {st.session_state.document_name}
                </div>
                <div class="document-type">
                    🔎 {st.session_state.document_type}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("📖 View extracted text"):
            st.text(st.session_state.document_text or "")

        st.markdown(
            '<div class="section-label">Document Actions</div>',
            unsafe_allow_html=True
        )

        document_type = st.session_state.document_type

        if document_type == "CV / Resume":

            if st.button("📝 Summarize CV", use_container_width=True):
                quick_request = "Summarize this CV."

            if st.button("🔑 Extract Skills", use_container_width=True):
                quick_request = "Extract the skills from this CV."

            if st.button("💼 Extract Experience", use_container_width=True):
                quick_request = "Extract the work experience from this CV."

            if st.button("🎓 Extract Education", use_container_width=True):
                quick_request = "Extract the education from this CV."

        elif document_type == "Meeting Notes":

            if st.button("📝 Summarize Meeting", use_container_width=True):
                quick_request = "Summarize these meeting notes."

            if st.button("🔑 Key Discussion Points", use_container_width=True):
                quick_request = (
                    "Extract the key discussion points from these meeting notes."
                )

            if st.button("✅ Action Items", use_container_width=True):
                quick_request = (
                    "Extract action items from these meeting notes."
                )

            if st.button("👤 Owners & Deadlines", use_container_width=True):
                quick_request = (
                    "Extract action items, owners and deadlines from these notes."
                )

        elif document_type == "Company Policy":

            if st.button("📝 Summarize Policy", use_container_width=True):
                quick_request = "Summarize this company policy."

            if st.button("🔑 Key Points", use_container_width=True):
                quick_request = "Extract the key points from this policy."

            if st.button("📅 Important Dates", use_container_width=True):
                quick_request = "Extract important dates from this policy."

            if st.button("❓ Ask Questions", use_container_width=True):
                quick_request = "Answer questions about this policy."

        else:

            if st.button("📝 Summarize Document", use_container_width=True):
                quick_request = "Summarize this document."

            if st.button("🔑 Extract Key Points", use_container_width=True):
                quick_request = "Extract the key points from this document."

            if st.button("📌 Extract Action Items", use_container_width=True):
                quick_request = "Extract action items from this document."


# =========================================
# PROCESS REQUEST
# =========================================

request = quick_request or user_request

if request:

    add_message(
        st.session_state.conversation,
        "user",
        request
    )

    conversation_history = get_recent_conversation(
        st.session_state.conversation,
        limit=6
    )

    normalized_request = request.lower()
    india_now = get_india_time()

    asks_time = any(
        phrase in normalized_request
        for phrase in [
            "current time",
            "what time",
            "time now",
            "local time",
            "check time",
            "time in india"
        ]
    )

    asks_date = any(
        phrase in normalized_request
        for phrase in [
            "today's date",
            "todays date",
            "current date",
            "what is the date",
            "date today",
            "check date",
            "date in india"
        ]
    )

    try:

        with st.spinner("🤖 Assistant is working..."):

            if asks_time and asks_date:
                response = (
                    f"Today's date in India is "
                    f"{india_now.strftime('%A, %d %B %Y')}. "
                    f"The current time is "
                    f"{india_now.strftime('%I:%M:%S %p')} IST."
                )

            elif asks_date:
                response = (
                    f"Today's date in India is "
                    f"{india_now.strftime('%A, %d %B %Y')}."
                )

            elif asks_time:
                response = (
                    f"The current time in India is "
                    f"{india_now.strftime('%I:%M:%S %p')} IST."
                )

            else:
                response = process_request(
                    request,
                    st.session_state.document_text,
                    conversation_history
                )

        if not isinstance(response, str):
            response = str(response)

    except Exception as error:
        st.error(f"The assistant encountered an error: {error}")
        response = (
            "Sorry, I could not process that request. "
            "Please check the assistant configuration and try again."
        )

    add_message(
        st.session_state.conversation,
        "assistant",
        response
    )

    st.rerun()


# =========================================
# EXAMPLE COMMANDS
# =========================================

with st.expander("💡 Example Commands"):

    example_col1, example_col2 = st.columns(2)

    with example_col1:

        st.markdown("**🏢 Company / RAG**")
        st.write("- What are the working hours?")
        st.write("- What is the leave policy?")
        st.write("- Which department handles IT issues?")

        st.markdown("**📧 Email Assistant**")
        st.write("- Draft an email requesting leave.")
        st.write("- Improve this email: ...")
        st.write("- Summarize this email: ...")

        st.markdown("**📋 Meeting Assistant**")
        st.write("- Create a meeting agenda for the AI team.")
        st.write("- Summarize these meeting notes.")
        st.write("- Extract action items from these notes.")

    with example_col2:

        st.markdown("**✅ Task Management**")
        st.write("- Create task Prepare project report")
        st.write("- Show my tasks")
        st.write("- Complete task 1")
        st.write("- Delete task 1")

        st.markdown("**📄 Document Intelligence**")
        st.write("- Upload a CV for CV analysis.")
        st.write("- Upload meeting notes for analysis.")
        st.write("- Upload a company policy for analysis.")

        st.markdown("**🧮 Tools**")
        st.write("- What is the current time?")
        st.write("- What is today's date?")
        st.write("- Calculate 76 * 9")


# =========================================
# FOOTER
# =========================================

st.divider()

st.markdown(
    '<div class="footer-text">'
    "AI Executive Office Assistant • "
    "RAG + LLM + Agent Orchestration + Tools"
    "</div>",
    unsafe_allow_html=True
)
