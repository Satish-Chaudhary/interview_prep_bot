import streamlit as st


def render_setup_page():
    st.markdown("<h1 style='margin-bottom:0;'>AI Interview Preparation Bot</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #64748B; font-size: 16px; margin-top: 0;'>"
        "Paste a job description, choose your level, and generate a tailored mock interview.</p>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("### Job Description")
        jd = st.text_area(
            "Paste the job description here",
            height=250,
            placeholder="Paste the full job description here (min 20 words, max 3,000 words)...",
            label_visibility="collapsed",
        )
        word_count = len(jd.split()) if jd.strip() else 0
        st.caption(f"Word count: {word_count} / 3,000")
        col1, col2 = st.columns(2)
        with col1:
            level = st.radio(
                "Knowledge Level",
                options=["Basic", "Medium", "Advanced"],
                index=1,
                horizontal=True,
                help="Basic = easier questions, Medium = mixed difficulty, Advanced = harder questions",
            )
        with col2:
            q_count = st.selectbox(
                "Number of Questions",
                options=[8, 10, 12, 15, 20],
                index=1,
            )

    with st.expander("Settings"):
        provider = st.selectbox(
            "AI Provider",
            options=["deepseek", "groq"],
            index=0,
            help="DeepSeek or Groq API for question generation and evaluation",
            key="provider_select",
        )

    st.session_state["jd_input"] = jd
    st.session_state["level"] = level
    st.session_state["question_count"] = q_count
    st.session_state["provider"] = provider

    can_generate = bool(jd.strip()) and word_count >= 20 and word_count <= 3000

    if st.button(
        "Generate Interview Questions",
        type="primary",
        use_container_width=True,
        disabled=not can_generate,
    ):
        if not can_generate:
            if word_count < 20:
                st.error("Job description is too short. Please provide at least 20 words.")
            elif word_count > 3000:
                st.error("Job description exceeds 3,000 words. Please shorten it.")
            return

        st.session_state["stage"] = "generating"
        st.rerun()

    return jd, level, q_count, provider
