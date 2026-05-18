import streamlit as st
from typing import Optional

from modules.assistant_bot import AssistantBot


@st.dialog("Clear Chat History?")
def _clear_chat_dialog():
    st.write("Are you sure you want to delete all messages with the Assistant Coach? This action cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Clear Chat", type="primary", use_container_width=True):
            st.session_state["assistant_messages"] = []
            st.rerun()


def render_assistant_sidebar():
    with st.sidebar:
        # Header with Clear Button
        col1, col2 = st.columns([3, 1], vertical_alignment="center")
        with col1:
            st.markdown("<h3 style='margin-bottom:0;'>✨ Assistant Coach</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("🗑️", use_container_width=True, help="Clear chat history"):
                _clear_chat_dialog()

        ok, msg = _check_provider()
        if not ok:
            st.warning(f"AI Provider not available: {msg}")
            return

        if "assistant_messages" not in st.session_state:
            st.session_state["assistant_messages"] = []

        context_enabled = st.toggle("Context: Current Question", value=True, help="Allow the assistant to see the question you are currently on.")
        
        current_stage = st.session_state.get("stage", "setup")

        # ChatGPT-like scrollable chat container
        chat_container = st.container(height=450, border=True)
        with chat_container:
            if not st.session_state["assistant_messages"]:
                st.markdown(
                    "<div style='text-align:center; padding-top: 40px; color:#94A3B8;'>"
                    "<h3>How can I help you?</h3>"
                    "<p>Ask for hints, concepts, or explanations.</p>"
                    "</div>",
                    unsafe_allow_html=True
                )
            
            for msg_data in st.session_state["assistant_messages"]:
                role = msg_data["role"]
                content = msg_data["content"]
                with st.chat_message(role):
                    st.markdown(content)
                    
            if st.session_state.get("pending_assistant_request"):
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        req = st.session_state["pending_assistant_request"]
                        _fetch_bot_response(req, context_enabled, stage=current_stage)
                st.session_state["pending_assistant_request"] = None
                st.rerun()

        # Quick Actions (Suggested Prompts)
        st.markdown("<p style='font-size:13px; color:#64748B; margin-bottom: 4px; margin-top: 8px;'><b>Suggested Prompts:</b></p>", unsafe_allow_html=True)
        
        if current_stage == "interview":
            quick_actions = ["Explain", "Hint", "Concepts"]
        else:
            quick_actions = ["Explain", "Sample", "Concepts"]
            
        c1, c2, c3 = st.columns(3)
        for i, action in enumerate(quick_actions):
            with [c1, c2, c3][i]:
                if st.button(action, key=f"qa_{i}", use_container_width=True):
                    # Map the short actions back to full prompts
                    prompt_map = {
                        "Explain": "Explain this question",
                        "Hint": "Give me a hint",
                        "Concepts": "Key concepts",
                        "Sample": "Give a sample answer"
                    }
                    req_text = prompt_map[action]
                    st.session_state["assistant_messages"].append({"role": "user", "content": req_text})
                    st.session_state["pending_assistant_request"] = req_text
                    st.rerun()

        # Fixed Chat Input at bottom
        if prompt := st.chat_input("Message Assistant Coach..."):
            st.session_state["assistant_messages"].append({"role": "user", "content": prompt})
            st.session_state["pending_assistant_request"] = prompt
            st.rerun()




@st.cache_resource
def _get_bot():
    try:
        return AssistantBot()
    except Exception as e:
        return None


@st.cache_data(ttl=10)
def _check_provider():
    bot = _get_bot()
    if bot is None:
        return False, "GROQ_API_KEY is not set. Get a free key at console.groq.com and add it to .env"
    return bot.is_available()


def _fetch_bot_response(text: str, context_enabled: bool, stage: Optional[str] = None):
    bot = _get_bot()
    if bot is None:
        st.session_state["assistant_messages"].append(
            {"role": "assistant", "content": "Error: Provider not configured (Missing API Key)."}
        )
        return

    current_q = None
    if context_enabled:
        q_idx = st.session_state.get("current_question_idx", 0)
        questions = st.session_state.get("questions", [])
        if q_idx < len(questions):
            current_q = questions[q_idx].get("question", "")

    try:
        response = bot.get_response(text, current_question=current_q, context_enabled=context_enabled, stage=stage)
        st.session_state["assistant_messages"].append({"role": "assistant", "content": response})
    except Exception as e:
        st.session_state["assistant_messages"].append(
            {"role": "assistant", "content": f"Error: {e}"}
        )
