import streamlit as st


def render_interview_page():
    questions = st.session_state.get("questions", [])
    answers = st.session_state.get("answers", [])
    evaluations = st.session_state.get("evaluations", {})
    current_idx = st.session_state.get("current_question_idx", 0)
    meta = st.session_state.get("meta", {})

    if not questions:
        st.warning("No questions generated yet.")
        if st.button("Back to Setup"):
            st.session_state["stage"] = "setup"
            st.rerun()
        return

    total = len(questions)
    q_obj = questions[current_idx]
    q_text = q_obj.get("question", "")
    category = q_obj.get("category", "")
    difficulty = q_obj.get("difficulty", "")

    st.markdown(f"<h2>Mock Interview</h2>", unsafe_allow_html=True)
    st.caption(f"Role: {meta.get('title', '')} | {meta.get('seniority', '')}")

    st.progress((current_idx + 1) / total, text=f"Question {current_idx + 1} of {total}")

    cat_colors = {
        "Technical": "#4F46E5",
        "Behavioral": "#2563EB",
        "Situational": "#06B6D4",
        "HR": "#64748B",
        "System Design": "#7C3AED",
    }
    cat_color = cat_colors.get(category, "#4F46E5")
    diff_icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(difficulty, "⚪")

    st.markdown(
        f"<div style='background:white;border:1px solid #E2E8F0;border-radius:12px;padding:20px;margin:16px 0;'>"
        f"<div style='display:flex;gap:8px;margin-bottom:12px;'>"
        f"<span style='background:{cat_color}20;color:{cat_color};padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600;'>{category}</span>"
        f"<span style='font-size:13px;'>{diff_icon} {difficulty}</span>"
        f"</div>"
        f"<h3 style='margin:0;font-size:18px;'>Q{current_idx + 1}. {q_text}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    current_answer = answers[current_idx] if current_idx < len(answers) else ""
    answer = st.text_area(
        "Your Answer",
        value=current_answer,
        height=200,
        key=f"answer_{current_idx}",
        placeholder="Type your answer here...",
    )

    if answer != current_answer:
        while len(answers) <= current_idx:
            answers.append("")
        answers[current_idx] = answer
        st.session_state["answers"] = answers

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("Previous", use_container_width=True, disabled=(current_idx == 0)):
            st.session_state["current_question_idx"] = current_idx - 1
            st.rerun()

    with col2:
        if st.button("Skip", use_container_width=True):
            skipped = st.session_state.get("skipped", [])
            if current_idx not in skipped:
                skipped.append(current_idx)
                st.session_state["skipped"] = skipped
            if current_idx < total - 1:
                st.session_state["current_question_idx"] = current_idx + 1
                st.rerun()

    with col3:
        if st.button("Evaluate", type="primary", use_container_width=True):
            if not answer.strip():
                st.warning("Please provide an answer before evaluating.")
            else:
                st.session_state["stage"] = "evaluating"
                st.session_state["eval_question_idx"] = current_idx
                st.rerun()

    with col4:
        if current_idx < total - 1:
            if st.button("Next", use_container_width=True):
                st.session_state["current_question_idx"] = current_idx + 1
                st.rerun()
        else:
            if st.button("Finish", type="primary", use_container_width=True):
                st.session_state["stage"] = "summary"
                st.rerun()

    if current_idx in st.session_state.get("evaluations", {}):
        ev = st.session_state["evaluations"][current_idx]
        if ev.get("success"):
            _render_evaluation(ev["data"])


def _render_evaluation(data: dict):
    score = data.get("score", 0)
    verdict = data.get("verdict", "")

    if score >= 8:
        vcolor = "#10B981"
    elif score >= 6:
        vcolor = "#2563EB"
    elif score >= 4:
        vcolor = "#F59E0B"
    else:
        vcolor = "#EF4444"

    st.markdown("---")
    st.markdown("### Evaluation")
    col_s, col_v = st.columns(2)
    col_s.metric("Score", f"{score}/10")
    col_v.markdown(
        f"<div style='background:{vcolor}20;color:{vcolor};padding:4px 16px;border-radius:20px;"
        f"font-weight:700;display:inline-block;margin-top:24px;'>{verdict}</div>",
        unsafe_allow_html=True,
    )

    strengths = data.get("strengths", [])
    if strengths:
        st.markdown("**What was good:**")
        for s in strengths:
            st.markdown(f"- {s}")

    missing = data.get("missing_concepts", [])
    if missing:
        st.markdown("**What's missing:**")
        for m in missing:
            st.markdown(f"- {m}")

    tips = data.get("improvement_suggestions", [])
    if tips:
        st.markdown("**How to improve:**")
        for t in tips:
            st.markdown(f"- {t}")

    ideal = data.get("ideal_answer", "")
    if ideal:
        with st.expander("Ideal Answer"):
            st.info(ideal)
