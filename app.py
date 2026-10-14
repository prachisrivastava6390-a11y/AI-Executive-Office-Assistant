from task_manager import tasks
import streamlit as st

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
# DOCUMENT TYPE DETECTION
# =========================================

def detect_document_type(document_text, document_name=""):

    text = document_text.lower() if document_text else ""
    filename = document_name.lower() if document_name else ""

    # =========================================
    # CV / RESUME SIGNALS
    # =========================================

    cv_keywords = [
        "resume",
        "curriculum vitae",
        "professional summary",
        "work experience",
        "experience",
        "education",
        "skills",
        "technical skills",
        "employment history",
        "career objective",
        "career summary",
        "professional experience",
        "projects",
        "certifications",
        "linkedin",
        "objective"
    ]

    cv_filename_keywords = [
        "resume",
        "cv",
        "curriculum",
        "profile"
    ]

    cv_score = sum(
        keyword in text
        for keyword in cv_keywords
    )

    cv_filename_score = sum(
        keyword in filename
        for keyword in cv_filename_keywords
    )


    # =========================================
    # MEETING NOTES SIGNALS
    # =========================================

    meeting_keywords = [
        "meeting",
        "meeting notes",
        "agenda",
        "attendees",
        "participant",
        "action items",
        "discussion",
        "decisions",
        "decision",
        "minutes of meeting",
        "minutes",
        "mom",
        "next steps",
        "follow up",
        "follow-up"
    ]

    meeting_filename_keywords = [
        "meeting",
        "minutes",
        "mom",
        "agenda"
    ]

    meeting_score = sum(
        keyword in text
        for keyword in meeting_keywords
    )

    meeting_filename_score = sum(
        keyword in filename
        for keyword in meeting_filename_keywords
    )


    # =========================================
    # COMPANY POLICY SIGNALS
    # =========================================

    policy_keywords = [
        "policy",
        "company policy",
        "leave policy",
        "attendance policy",
        "work from home",
        "code of conduct",
        "employee policy",
        "guidelines",
        "procedure",
        "eligibility",
        "compliance",
        "rules and regulations"
    ]

    policy_filename_keywords = [
        "policy",
        "guideline",
        "procedure",
        "rules"
    ]

    policy_score = sum(
        keyword in text
        for keyword in policy_keywords
    )

    policy_filename_score = sum(
        keyword in filename
        for keyword in policy_filename_keywords
    )


    # =========================================
    # COMBINE SCORES
    # =========================================

    scores = {
        "CV / Resume": (
            cv_score + (cv_filename_score * 3)
        ),

        "Meeting Notes": (
            meeting_score + (meeting_filename_score * 3)
        ),

        "Company Policy": (
            policy_score + (policy_filename_score * 3)
        )
    }


    # =========================================
    # DETERMINE TYPE
    # =========================================

    detected_type = max(
        scores,
        key=scores.get
    )

    highest_score = scores[detected_type]


    # =========================================
    # FALLBACK
    # =========================================

    if highest_score < 2:
        return "General Document"

    return detected_type


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

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

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

# Get live task statistics
total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks
    if task["status"] == "Completed"
)

pending_tasks = sum(
    1 for task in tasks
    if task["status"] == "Pending"
)

# Display dashboard metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📋 Total Tasks", total_tasks)

with col2:
    st.metric("⏳ Pending Tasks", pending_tasks)

with col3:
    st.metric("✅ Completed Tasks", completed_tasks)

with col4:
    message_count = len(
        st.session_state.get("conversation", [])
    )
    st.metric("💬 Messages", message_count)

# Get conversation statistics
conversation = st.session_state.get(
    "conversation", []
)

message_count = len(conversation)

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

    if st.button(
        "🕐 Check Time",
        use_container_width=True
    ):

        quick_request = "What is the current time?"


with quick_col2:

    if st.button(
        "📅 Check Date",
        use_container_width=True
    ):

        quick_request = "What is today's date?"


with quick_col3:

    if st.button(
        "🏢 Company Policies",
        use_container_width=True
    ):

        quick_request = "What are the company policies?"


with quick_col4:

    if st.button(
        "🧮 Calculator",
        use_container_width=True
    ):

        st.session_state.calculator_open = (
            not st.session_state.calculator_open
        )


# =========================================
# CALCULATOR
# =========================================

if st.session_state.calculator_open:

    calculator_col1, calculator_col2 = st.columns(
        [4, 1]
    )

    with calculator_col1:

        calculator_expression = st.text_input(
            "Calculation",
            placeholder="Example: 76 * 9",
            label_visibility="collapsed"
        )

    with calculator_col2:

        if st.button(
            "Calculate",
            use_container_width=True
        ):

            if calculator_expression:

                quick_request = (
                    f"Calculate {calculator_expression}"
                )


st.divider()


# =========================================
# MAIN WORKSPACE
# =========================================

chat_col, document_col = st.columns(
    [2.2, 1],
    gap="large"
)


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


    # -----------------------------------------
    # CONVERSATION
    # -----------------------------------------

    if st.session_state.conversation:

        for message in st.session_state.conversation:

            role = message["role"]
            content = message["content"]

            if role == "user":

                with st.chat_message("user"):
                    st.write(content)

            else:

                with st.chat_message("assistant"):
                    st.write(content)

    else:

        st.info(
            "👋 Start a conversation by asking me something below."
        )


    st.write("")


    # -----------------------------------------
    # CHAT INPUT
    # -----------------------------------------

    user_request = st.chat_input(
        "Ask your assistant..."
    )


# =========================================
# DOCUMENT AREA
# =========================================

with document_col:

    st.markdown(
        '<div class="chat-header">📄 Documents</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "Upload a PDF, DOCX, or TXT file for analysis."
    )


    # -----------------------------------------
    # FILE UPLOAD
    # -----------------------------------------

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )


    # -----------------------------------------
    # PROCESS DOCUMENT
    # -----------------------------------------

    if uploaded_file:

        if (
            st.session_state.document_name
            != uploaded_file.name
        ):

            try:

                document_text = extract_document_text(
                    uploaded_file
                )

                st.session_state.document_text = (
                    document_text
                )

                st.session_state.document_name = (
                    uploaded_file.name
                )

                # IMPORTANT:
                # Pass both text and filename
                # to the detector.

                st.session_state.document_type = (
                    detect_document_type(
                        document_text,
                        uploaded_file.name
                    )
                )

            except Exception as error:

                st.error(
                    f"Could not process the document: {error}"
                )


    # -----------------------------------------
    # ACTIVE DOCUMENT
    # -----------------------------------------

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


        # -------------------------------------
        # EXTRACTED TEXT
        # -------------------------------------

        with st.expander(
            "📖 View extracted text"
        ):

            st.write(
                st.session_state.document_text
            )


        # -------------------------------------
        # DOCUMENT ACTIONS
        # -------------------------------------

        st.markdown(
            '<div class="section-label">Document Actions</div>',
            unsafe_allow_html=True
        )

        document_type = (
            st.session_state.document_type
        )


        # =====================================
        # CV / RESUME
        # =====================================

        if document_type == "CV / Resume":

            if st.button(
                "📝 Summarize CV",
                use_container_width=True
            ):

                quick_request = (
                    "Summarize this CV"
                )


            if st.button(
                "🔑 Extract Skills",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the skills from this CV"
                )


            if st.button(
                "💼 Extract Experience",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the work experience "
                    "from this CV"
                )


            if st.button(
                "🎓 Extract Education",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the education "
                    "from this CV"
                )


        # =====================================
        # MEETING NOTES
        # =====================================

        elif document_type == "Meeting Notes":

            if st.button(
                "📝 Summarize Meeting",
                use_container_width=True
            ):

                quick_request = (
                    "Summarize this meeting"
                )


            if st.button(
                "🔑 Key Discussion Points",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the key discussion "
                    "points from these meeting notes"
                )


            if st.button(
                "✅ Action Items",
                use_container_width=True
            ):

                quick_request = (
                    "Extract action items from "
                    "these meeting notes"
                )


            if st.button(
                "👤 Owners & Deadlines",
                use_container_width=True
            ):

                quick_request = (
                    "Extract action items, owners "
                    "and deadlines from these "
                    "meeting notes"
                )


        # =====================================
        # COMPANY POLICY
        # =====================================

        elif document_type == "Company Policy":

            if st.button(
                "📝 Summarize Policy",
                use_container_width=True
            ):

                quick_request = (
                    "Summarize this policy"
                )


            if st.button(
                "🔑 Key Points",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the key points "
                    "from this policy"
                )


            if st.button(
                "📅 Important Dates",
                use_container_width=True
            ):

                quick_request = (
                    "Extract important dates "
                    "from this policy"
                )


            if st.button(
                "❓ Ask Questions",
                use_container_width=True
            ):

                quick_request = (
                    "Answer questions about "
                    "this policy"
                )


        # =====================================
        # GENERAL DOCUMENT
        # =====================================

        else:

            if st.button(
                "📝 Summarize Document",
                use_container_width=True
            ):

                quick_request = (
                    "Summarize this document"
                )


            if st.button(
                "🔑 Extract Key Points",
                use_container_width=True
            ):

                quick_request = (
                    "Extract the key points "
                    "from this document"
                )


            if st.button(
                "📌 Extract Action Items",
                use_container_width=True
            ):

                quick_request = (
                    "Extract action items "
                    "from this document"
                )


# =========================================
# PROCESS REQUEST
# =========================================

request = quick_request or user_request


if request:

    # -----------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------

    add_message(
        st.session_state.conversation,
        "user",
        request
    )


    # -----------------------------------------
    # GET CONVERSATION HISTORY
    # -----------------------------------------

    conversation_history = get_recent_conversation(
        st.session_state.conversation,
        limit=6
    )


    # -----------------------------------------
    # AI RESPONSE
    # -----------------------------------------

    with st.spinner(
        "🤖 Assistant is working..."
    ):

        response = process_request(
            request,
            st.session_state.document_text,
            conversation_history
        )


    # -----------------------------------------
    # SAVE ASSISTANT RESPONSE
    # -----------------------------------------

    add_message(
        st.session_state.conversation,
        "assistant",
        response
    )


    # -----------------------------------------
    # REFRESH
    # -----------------------------------------

    st.rerun()


# =========================================
# EXAMPLE COMMANDS
# =========================================

with st.expander(
    "💡 Example Commands"
):

    example_col1, example_col2 = st.columns(2)


    with example_col1:

        st.markdown("**🏢 Company / RAG**")

        st.write(
            "- What are the working hours?"
        )

        st.write(
            "- What is the leave policy?"
        )

        st.write(
            "- Which department handles IT issues?"
        )


        st.markdown("**📧 Email Assistant**")

        st.write(
            "- Draft an email requesting leave."
        )

        st.write(
            "- Improve this email: ..."
        )

        st.write(
            "- Summarize this email: ..."
        )


        st.markdown("**📋 Meeting Assistant**")

        st.write(
            "- Create a meeting agenda for the AI team."
        )

        st.write(
            "- Summarize these meeting notes: ..."
        )

        st.write(
            "- Extract action items from these notes."
        )


    with example_col2:

        st.markdown("**✅ Task Management**")

        st.write(
            "- Create task Prepare project report"
        )

        st.write(
            "- Show my tasks"
        )

        st.write(
            "- Complete task 1"
        )

        st.write(
            "- Delete task 1"
        )


        st.markdown("**📄 Document Intelligence**")

        st.write(
            "- Upload a CV for CV analysis"
        )

        st.write(
            "- Upload meeting notes for meeting analysis"
        )

        st.write(
            "- Upload a company policy for policy analysis"
        )


        st.markdown("**🧮 Tools**")

        st.write(
            "- What is the current time?"
        )

        st.write(
            "- What is today's date?"
        )

        st.write(
            "- Calculate 76 * 9"
        )


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
