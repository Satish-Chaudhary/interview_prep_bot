import streamlit as st
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from difflib import SequenceMatcher

from modules.answer_evaluator import evaluate_answer
from modules.config import validate_env, get_provider_name, get_active_model_name
from modules.interview_session import InterviewSession
from modules.pdf_generator import generate_pdf_report, get_pdf_filename
from modules.question_generator import generate_questions
from modules.providers.factory import get_available_providers
from modules.ui.assistant_sidebar import render_assistant_sidebar
from modules.voice_analyzer import analyze_filler_words

st.set_page_config(
    page_title="AI Interview Prep Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] { font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; }
    
    /* Lock the viewport so the entire page never scrolls */
    html, body, .stApp {
        height: 100vh !important;
        overflow: hidden !important;
    }
    
    /* Make the main content block scrollable internally instead of page scroll */
    .block-container { 
        max-width: 1100px; 
        padding: 2rem 3rem !important; /* Padding all around */
        height: 100vh;
        overflow-y: auto !important;
        padding-bottom: 4rem !important;
    }

    /* Target sidebar explicitly to give it nice breathing room */
    [data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1.5rem !important;
        padding-bottom: 3.5rem !important;
    }

    /* Prevent the sidebar itself from scrolling, and force the chat box to flex height */
    [data-testid="stSidebar"] > div:first-child {
        overflow: hidden !important;
    }
    
    /* Target the chat container and make it dynamic height */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        height: calc(100vh - 300px) !important;
        overflow-y: auto !important;
    }

    .stApp { background-color: #F8FAFC; }
    div[data-testid="stExpander"] { border: 1px solid #E2E8F0; border-radius: 8px; }
    .stProgress > div > div { background-color: #4F46E5; }
    .stButton > button[kind="primary"] { background-color: #4F46E5; border: none; }
    .stButton > button[kind="primary"]:hover { background-color: #312E81; }
    .stButton > button[kind="secondary"] { border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)


def _init_state():
    defaults = {
        "stage": "setup",
        "questions": [],
        "answers": [],
        "evaluations": {},
        "skipped": [],
        "current_question_idx": 0,
        "session": None,
        "meta": {},
        "summary": None,
        "pdf_bytes": None,
        "generation_error": None,
        "eval_question_idx": None,
        "jd_input": "",
        "level": "Medium",
        "question_count": 10,
        "provider": get_provider_name(),
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()


def _check_env_warnings():
    warnings = validate_env()
    if warnings:
        with st.sidebar:
            for w in warnings:
                st.warning(f"⚠️ {w}")


def _render_setup():
    available_providers = get_available_providers()
    provider_options = [p[0] for p in available_providers]
    provider_labels = {p[0]: p[1] for p in available_providers}
    
    default_provider = st.session_state.get("provider", get_provider_name())
    if default_provider not in provider_options:
        default_provider = provider_options[0] if provider_options else "groq"


    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h1 style='margin-bottom:0;'>AI Interview Preparation Bot</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color: #64748B; font-size: 16px; margin-top: 0;'>"
            "Paste a job description, choose your level, and generate a tailored mock interview.</p>",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state["stage"] = "dashboard"
            st.rerun()
            
        st.markdown("<br>", unsafe_allow_html=True)
        provider = st.selectbox(
            "AI Provider",
            options=provider_options,
            format_func=lambda x: provider_labels.get(x, x),
            index=provider_options.index(default_provider) if default_provider in provider_options else 0,
            help="Core AI provider",
            key="provider_select",
        )
        active_model = get_active_model_name(provider)
        st.caption(f"🧠 Active Model: `{active_model}`")

        stress_mode = st.toggle("Stress Mode (Timed)", value=st.session_state.get("stress_mode", False))
        if stress_mode:
            time_duration = st.number_input(
                "Duration (min)",
                min_value=1,
                max_value=10,
                value=st.session_state.get("time_duration", 2),
                step=1,
                help="Set time limit per question"
            )
            st.session_state["time_duration"] = time_duration
        else:
            st.session_state["time_duration"] = 2


    with st.container():
        st.markdown("### Job Description")
        jd = st.text_area(
            "Job Description",
            height=250,
            placeholder="Paste the full job description here (min 20 words, max 3,000 words)...",
            label_visibility="collapsed",
            key="jd_input",
        )
        word_count = len(jd.split()) if jd.strip() else 0
        st.caption(f"Word count: {word_count} / 3,000")

        col1, col2 = st.columns(2)
        with col1:
            level = st.radio(
                "Knowledge Level",
                options=["Easy", "Medium", "Hard"],
                index=1,
                horizontal=True,
                help="Easy = foundational, Medium = mixed, Hard = advanced/scenario-based",
            )
        with col2:
            q_count = st.selectbox(
                "Number of Questions",
                options=[8, 10, 12, 15, 20],
                index=1,
            )

    st.session_state["stress_mode"] = stress_mode
    st.session_state["level"] = level
    st.session_state["question_count"] = q_count
    st.session_state["provider"] = provider

    can_generate = bool(jd.strip()) and word_count >= 20

    if not can_generate and jd.strip():
        if word_count < 20:
            st.warning(f"⚠️ Need {20 - word_count} more words to enable generation.")

    if st.button(
        "Generate Interview Questions",
        type="primary",
        use_container_width=True,
        disabled=not can_generate,
    ):
        if not can_generate:
            return
        
        if word_count > 3000:
            st.error("Job description exceeds 3,000 words. Please shorten it.")
            return

        st.session_state["generation_status"] = "generating"
        st.session_state["generation_result"] = None
        
        ctx = get_script_run_ctx()
        def _bg_generate():
            add_script_run_ctx(ctx=ctx)
            try:
                res = generate_questions(
                    job_description=jd,
                    level=level,
                    question_count=q_count,
                    provider_name=provider,
                )
                st.session_state["generation_result"] = res
            except Exception as e:
                st.session_state["generation_result"] = {"success": False, "error": str(e)}
        
        threading.Thread(target=_bg_generate).start()

        st.session_state["stage"] = "instructions"
        st.rerun()

    if st.session_state.get("generation_error"):
        st.error(f"Generation failed: {st.session_state['generation_error']}")
        if st.button("Try Again"):
            st.session_state["generation_error"] = None
            st.rerun()

@st.fragment(run_every=2)
def _check_generation():
    if st.session_state.get("generation_status") == "generating":
        if st.session_state.get("generation_result") is not None:
            st.session_state["generation_status"] = "done"
            st.rerun()

def _render_instructions():
    st.markdown("<h2>Interview Rules & Instructions</h2>", unsafe_allow_html=True)
    
    st.info("Please read the following rules carefully before starting the mock interview.")
    
    st.markdown("""
    ### 🛑 Strict Anti-Cheat System Enabled
    This mock interview enforces strict evaluation rules to simulate a real, proctored interview environment:
    
    1. **Tab & Window Monitoring:** Switching tabs, minimizing the window, or navigating away will be instantly detected and recorded. Multiple violations may lead to disqualification.
    2. **Right-Click & Dev Tools Blocked:** For security, right-clicking is disabled, and Developer Tools (F12, Ctrl+Shift+I) are restricted. Any attempt to inspect the app will trigger an alert.
    3. **Copy-Paste Restrictions:** You cannot paste external content into your answer area, nor can you copy text from the Assistant Coach. You must type your answers manually.
    4. **Skipped or Empty Answers = 0 Score:** Answering with 'I don't know' or leaving the field blank will result in a 0 for that question, severely impacting your performance report.
    5. **External AI Detection:** The AI evaluator is trained to spot answers generated by ChatGPT or other LLMs. If perfectly structured artificial text is detected, your score will be penalized.
    """)
    
    st.markdown("---")
    
    status = st.session_state.get("generation_status", "idle")
    
    if status == "generating":
        st.info("⏳ Analyzing job description and generating questions... Please wait.")
        if st.button("I understand, Start Interview ✅", type="primary", use_container_width=True):
            if st.session_state.get("generation_result") is not None:
                st.session_state["generation_status"] = "done"
                st.rerun()
            else:
                st.toast("We are preparing your interview. It takes some time / a little bit.", icon="⏳")
        _check_generation()
        
    elif status == "done":
        res = st.session_state.get("generation_result", {})
        if res.get("success"):
            st.success("✅ Questions are ready!")
            if st.button("I understand, Start Interview ✅", type="primary", use_container_width=True):
                data = res["data"]
                questions = data.get("questions", [])
                st.session_state["questions"] = questions
                st.session_state["answers"] = ["" for _ in questions]
                st.session_state["evaluations"] = {}
                st.session_state["skipped"] = []
                st.session_state["current_question_idx"] = 0
                st.session_state["meta"] = {
                    "title": data.get("title", "Interview"),
                    "role": data.get("role", ""),
                    "seniority": data.get("seniority", ""),
                    "key_skills": data.get("key_skills", []),
                    "jd_analysis": data.get("jd_analysis", {}),
                }
                sess = InterviewSession()
                sess.start(questions, st.session_state["meta"])
                st.session_state["session"] = sess
                st.session_state["summary"] = None
                st.session_state["pdf_bytes"] = None
                st.session_state["stage"] = "interview"
                st.rerun()
        else:
            st.error(f"Generation failed: {res.get('error')}")
            if st.button("Cancel & Go Back", key="btn_cancel_err"):
                st.session_state["stage"] = "setup"
                st.rerun()
        
    if st.button("Cancel & Go Back", key="btn_cancel_main"):
        st.session_state["stage"] = "setup"
        st.rerun()


def _render_interview():
    questions = st.session_state.get("questions", [])
    answers = st.session_state.get("answers", [])
    evaluations = st.session_state.get("evaluations", {})
    idx = st.session_state.get("current_question_idx", 0)
    meta = st.session_state.get("meta", {})

    if not questions:
        st.warning("No questions. Go back to setup.")
        if st.button("Back to Setup"):
            st.session_state["stage"] = "setup"
            st.rerun()
        return

    total = len(questions)
    q_obj = questions[idx]

    # Just-In-Time Generation
    if q_obj.get("question") == "Loading dynamically...":
        with st.spinner("Generating next question dynamically based on your performance..."):
            from modules.question_generator import generate_dynamic_question
            
            # get previous score if available
            prev_idx = str(idx - 1)
            prev_score = -1.0
            if prev_idx in evaluations and evaluations[prev_idx].get("success"):
                prev_score = evaluations[prev_idx]["data"].get("score", -1.0)
            
            jd_analysis = st.session_state.get("meta", {}).get("jd_analysis", {})
            level = st.session_state.get("level", "Medium")
            
            res = generate_dynamic_question(
                jd_analysis=jd_analysis,
                level=level,
                previous_score=prev_score,
                provider_name=st.session_state.get("provider")
            )
            
            if res.get("success"):
                new_q = res["data"]
                new_q["id"] = idx + 1
                questions[idx] = new_q
                st.session_state["questions"] = questions
                q_obj = new_q
            else:
                st.error("Failed to generate the next question. Please try navigating again.")
                return

    q_text = q_obj.get("question", "")
    category = q_obj.get("category", "")
    difficulty = q_obj.get("difficulty", "")

    st.markdown("<h2>Mock Interview</h2>", unsafe_allow_html=True)
    st.caption(f"Role: {meta.get('title', '')} | {meta.get('seniority', '')}")

    st.progress((idx + 1) / total, text=f"Question {idx + 1} of {total}")

    cat_colors = {
        "Technical": "#4F46E5", "Behavioral": "#2563EB",
        "Situational": "#06B6D4", "HR": "#64748B",
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
        f"<h3 style='margin:0;font-size:18px;'>Q{idx + 1}. {q_text}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    has_evaluated = str(idx) in evaluations
    if st.session_state.get("stress_mode", False) and not has_evaluated:
        duration_mins = st.session_state.get("time_duration", 2)
        total_seconds = int(duration_mins * 60)
        import streamlit.components.v1 as components
        components.html(
            f"""
            <div id="timer" style="font-size:20px; color:#EF4444; font-weight:bold; font-family: sans-serif; text-align: center; border: 2px solid #EF4444; border-radius: 8px; padding: 8px; background: #FEF2F2; width: 120px; margin: 0 auto;">{duration_mins}:00</div>
            <script>
                var timeLeft = {total_seconds};
                var elem = document.getElementById('timer');
                var timerId = setInterval(function() {{
                    if (timeLeft <= 0) {{
                        clearInterval(timerId);
                        elem.innerHTML = "TIME'S UP!";
                        var textareas = window.parent.document.querySelectorAll('textarea');
                        for (var i=0; i<textareas.length; i++) {{
                            textareas[i].blur();
                        }}
                        setTimeout(function() {{
                            var buttons = window.parent.document.querySelectorAll('button');
                            for (var i=0; i<buttons.length; i++) {{
                                if (buttons[i].innerText.includes('Evaluate')) {{
                                    buttons[i].click();
                                    break;
                                }}
                            }}
                        }}, 500);
                    }} else {{
                        var m = Math.floor(timeLeft / 60);
                        var s = (timeLeft % 60).toString().padStart(2, '0');
                        elem.innerHTML = "⏳ " + m + ":" + s;
                        timeLeft--;
                    }}
                }}, 1000);
            </script>
            """,
            height=60
        )

    current_answer = answers[idx] if idx < len(answers) else ""

    # Inject Anti-Cheat JS here
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            const parentDoc = window.parent.document;
            const parentWindow = window.parent;

            parentDoc.addEventListener("visibilitychange", () => {
                if (parentDoc.hidden) {
                    alert("🚨 ANTI-CHEAT WARNING: Tab switching or minimizing the window is prohibited during the active interview!");
                }
            });

            parentWindow.addEventListener("blur", () => {
                console.log("Window lost focus. User might be looking at another application.");
            });

            parentDoc.addEventListener("copy", (e) => {
                alert("🚨 ANTI-CHEAT WARNING: Copying text is disabled during the interview.");
                e.preventDefault();
            });

            parentDoc.addEventListener("paste", (e) => {
                if (e.target.tagName.toLowerCase() === 'textarea') {
                    alert("🚨 ANTI-CHEAT WARNING: Pasting answers is strictly prohibited!");
                    e.preventDefault();
                }
            });

            parentDoc.addEventListener("contextmenu", (e) => {
                alert("🚨 ANTI-CHEAT WARNING: Right-click is disabled during the interview!");
                e.preventDefault();
            });

            parentDoc.addEventListener("keydown", (e) => {
                // F12
                if (e.key === "F12") {
                    alert("🚨 ANTI-CHEAT WARNING: Developer tools are disabled!");
                    e.preventDefault();
                }
                // Ctrl+Shift+I or Cmd+Option+I
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "I" || e.key === "i")) {
                    alert("🚨 ANTI-CHEAT WARNING: Developer tools are disabled!");
                    e.preventDefault();
                }
                // Ctrl+Shift+J or Cmd+Option+J
                if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === "J" || e.key === "j")) {
                    alert("🚨 ANTI-CHEAT WARNING: Developer tools are disabled!");
                    e.preventDefault();
                }
                // Ctrl+U or Cmd+U (View Source)
                if ((e.ctrlKey || e.metaKey) && (e.key === "U" || e.key === "u")) {
                    alert("🚨 ANTI-CHEAT WARNING: Viewing source is disabled!");
                    e.preventDefault();
                }
            });
        </script>
        """,
        height=0,
        width=0,
    )

    answer = st.text_area(
        "Your Answer",
        value=current_answer,
        height=200,
        key=f"q_{idx}",
        help="Type your answer here. Note: Copy-pasting is strictly prohibited.",
    )

    if answer != current_answer:
        while len(answers) <= idx:
            answers.append("")
        answers[idx] = answer
        st.session_state["answers"] = answers

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        if st.button("⬅ Previous", use_container_width=True, disabled=(idx == 0)):
            st.session_state["current_question_idx"] = idx - 1
            st.rerun()

    with col2:
        if st.button("⏭ Skip", use_container_width=True):
            skipped = st.session_state.get("skipped", [])
            if idx not in skipped:
                skipped.append(idx)
                st.session_state["skipped"] = skipped
            if idx < total - 1:
                st.session_state["current_question_idx"] = idx + 1
                st.rerun()

    with col3:
        eval_key = f"eval_{idx}"
        if st.button("Evaluate", type="primary", use_container_width=True, key=eval_key):
            # 🛑 Phase 2: Copy-Paste Detection
            is_cheating = False
            assistant_msgs = st.session_state.get("assistant_messages", [])
            for msg in assistant_msgs:
                if msg["role"] == "assistant" and answer.strip():
                    # Compare user answer to assistant message (ignoring case)
                    ratio = SequenceMatcher(None, answer.lower().strip(), msg["content"].lower().strip()).ratio()
                    if ratio > 0.8:
                        is_cheating = True
                        break

            if is_cheating:
                st.toast("🚨 Warning: Cheating Detected! Copy-pasting from Assistant is prohibited.", icon="🚨")
                st.error("Cheating Detected! Copying answers from the Assistant Coach is not allowed. Score set to 0.")
                result = {
                    "success": True,
                    "data": {
                        "score": 0,
                        "verdict": "Cheating Detected",
                        "strengths": [],
                        "missing_concepts": ["Originality"],
                        "improvement_suggestions": ["Do not copy answers from the Assistant Coach. Answer in your own words."],
                        "ideal_answer": "An answer written from your own understanding."
                    }
                }
            else:
                with st.spinner("Evaluating your answer..."):
                    result = evaluate_answer(
                        question=q_text,
                        answer=answer,
                        category=category,
                        provider_name=st.session_state.get("provider"),
                    )
                    
                    # 🛑 Phase 4: Filler Word Analysis
                    if result.get("success") and answer.strip():
                        filler_analysis = analyze_filler_words(answer)
                        if filler_analysis["total"] > 0 and filler_analysis["feedback"]:
                            # Append the filler word feedback to the improvement suggestions
                            result["data"]["improvement_suggestions"].append(filler_analysis["feedback"])
            
            evaluations[str(idx)] = result
            st.session_state["evaluations"] = evaluations
            st.rerun()

    with col4:
        if idx < total - 1:
            if st.button("Next ➡", use_container_width=True):
                st.session_state["current_question_idx"] = idx + 1
                st.rerun()
        else:
            if st.button("Finish ✅", type="primary", use_container_width=True):
                st.session_state["stage"] = "summarizing"
                st.rerun()

    if str(idx) in evaluations:
        ev = evaluations[str(idx)]
        if ev.get("success"):
            _show_evaluation(ev["data"])
        else:
            st.error(f"Evaluation failed: {ev.get('error', '')}")

    st.markdown("---")
    nav_cols = st.columns(min(total, 10))
    for qi in range(total):
        is_answered = answers[qi] if qi < len(answers) else ""
        is_skipped = qi in st.session_state.get("skipped", [])
        icon = "⏭" if is_skipped else ("✅" if is_answered.strip() else "◯")
        if nav_cols[qi % len(nav_cols)].button(f"{icon} {qi+1}", key=f"nav_{qi}"):
            st.session_state["current_question_idx"] = qi
            st.rerun()


def _show_evaluation(data: dict):
    score = data.get("score", 0)
    verdict = data.get("verdict", "")
    vcolor = "#10B981" if score >= 8 else ("#2563EB" if score >= 6 else ("#F59E0B" if score >= 4 else "#EF4444"))

    st.markdown("---")
    st.markdown("### Evaluation")
    c1, c2 = st.columns(2)
    c1.metric("Score", f"{score}/10")
    c2.markdown(
        f"<div style='background:{vcolor}20;color:{vcolor};padding:4px 16px;"
        f"border-radius:20px;font-weight:700;display:inline-block;margin-top:24px;'>{verdict}</div>",
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


def _render_summary():
    questions = st.session_state.get("questions", [])
    answers = st.session_state.get("answers", [])
    evaluations = st.session_state.get("evaluations", {})
    meta = st.session_state.get("meta", {})

    st.markdown("<h2>Interview Summary</h2>", unsafe_allow_html=True)

    if not st.session_state.get("summary"):
        with st.spinner("Generating your performance summary..."):
            sess = st.session_state.get("session")
            if sess:
                all_evals = []
                for i in range(len(questions)):
                    ev = evaluations.get(str(i))
                    if ev:
                        all_evals.append(ev)
                    else:
                        all_evals.append({"success": False})
                sess.store_evaluations(all_evals)
                summary = sess.generate_summary(provider_name=st.session_state.get("provider"))
                st.session_state["summary"] = summary

    summary = st.session_state.get("summary", {})
    overall = float(summary.get("overall_score", 0))
    readiness = summary.get("readiness", "N/A")

    rcolor = "#10B981" if overall >= 70 else ("#2563EB" if overall >= 50 else ("#F59E0B" if overall >= 30 else "#EF4444"))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div style='text-align:center;padding:20px;background:white;border:1px solid #E2E8F0;"
            f"border-radius:12px;'>"
            f"<div style='font-size:36px;font-weight:700;color:{rcolor};'>{overall:.0f}<span style='font-size:20px;color:#94A3B8;'> / 100</span></div>"
            f"<div style='color:#64748B;'>Overall Score</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div style='text-align:center;padding:20px;background:white;border:1px solid #E2E8F0;"
            f"border-radius:12px;'>"
            f"<div style='font-size:24px;font-weight:600;color:{rcolor};'>{readiness}</div>"
            f"<div style='color:#64748B;'>Readiness Level</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        answered = sum(1 for a in answers if a and a.strip())
        st.markdown(
            f"<div style='text-align:center;padding:20px;background:white;border:1px solid #E2E8F0;"
            f"border-radius:12px;'>"
            f"<div style='font-size:24px;font-weight:600;color:#4F46E5;'>{answered}/{len(questions)}</div>"
            f"<div style='color:#64748B;'>Questions Answered</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### Strong Areas")
        strong = summary.get("strong_areas", [])
        if strong:
            for s in strong:
                st.markdown(f"- ✅ {s}")
        else:
            st.caption("No strong areas identified.")

    with col_r:
        st.markdown("### Areas to Improve")
        weak = summary.get("weak_areas", [])
        if weak:
            for w in weak:
                st.markdown(f"- ⚠️ {w}")
        else:
            st.caption("No weak areas identified.")

    recs = summary.get("recommendations", [])
    if recs:
        st.markdown("### Improvement Plan")
        for i, rec in enumerate(recs, 1):
            st.markdown(f"{i}. {rec}")

    st.markdown("---")
    st.markdown("### Question Details")
    for i, q_obj in enumerate(questions):
        q_text = q_obj.get("question", f"Q{i+1}")
        ev = evaluations.get(str(i), {})
        with st.expander(f"Q{i+1}. {q_text[:100]}..." if len(q_text) > 100 else f"Q{i+1}. {q_text}"):
            ans = answers[i] if i < len(answers) else ""
            st.markdown(f"**Your answer:** {ans or '_Skipped_'}")
            if ev.get("success"):
                d = ev.get("data", {})
                st.markdown(f"**Score:** {d.get('score', '?')}/10 | **Verdict:** {d.get('verdict', '?')}")

    st.markdown("---")

    if not st.session_state.get("pdf_bytes"):
        with st.spinner("Generating PDF..."):
            all_evals_list = []
            for i in range(len(questions)):
                ev = evaluations.get(str(i), {})
                all_evals_list.append(ev)
            pdf_bytes = generate_pdf_report(
                questions=questions,
                answers=answers,
                evaluations=all_evals_list,
                summary=summary,
                meta=meta,
            )
            st.session_state["pdf_bytes"] = pdf_bytes

    pdf_bytes = st.session_state["pdf_bytes"]
    filename = get_pdf_filename(meta)

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    st.markdown("---")
    c_a, c_b = st.columns(2)
    with c_a:
        if st.button("Restart Interview", use_container_width=True):
            sess = st.session_state.get("session")
            if sess:
                sess.restart()
            st.session_state["answers"] = ["" for _ in st.session_state["questions"]]
            st.session_state["evaluations"] = {}
            st.session_state["skipped"] = []
            st.session_state["current_question_idx"] = 0
            st.session_state["summary"] = None
            st.session_state["pdf_bytes"] = None
            st.session_state["stage"] = "interview"
            st.rerun()
    with c_b:
        if st.button("New Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            _init_state()
            st.rerun()


def _render_dashboard():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("<h1 style='margin-bottom:0;'>Interview Analytics Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B;'>Review your past performance and track your growth.</p>", unsafe_allow_html=True)
    with col2:
        if st.button("⬅️ Back to Setup", use_container_width=True):
            st.session_state["stage"] = "setup"
            st.rerun()
            
    st.divider()
    
    from modules.database import get_all_interviews
    try:
        interviews = get_all_interviews()
    except Exception as e:
        st.error("Failed to load database.")
        return
        
    if not interviews:
        st.info("No interview history found. Complete a mock interview to see your analytics here!")
        return
        
    # Stats row
    avg_score = sum(i['final_score'] for i in interviews) / len(interviews)
    total_q = sum(i['question_count'] for i in interviews)
    
    st_cols = st.columns(3)
    st_cols[0].metric("Total Mock Interviews", len(interviews))
    st_cols[1].metric("Average Score", f"{avg_score:.1f}/100")
    st_cols[2].metric("Questions Answered", total_q)
    
    st.markdown("### Interview History")
    for idx, interview in enumerate(interviews):
        with st.expander(f"Interview #{len(interviews)-idx} - {interview['date']} | Score: {interview['final_score']}/100"):
            st.write(f"**Level:** {interview['level']} | **Questions:** {interview['question_count']} | **Verdict:** {interview['readiness_level']}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**👍 Strengths:**")
                for s in interview['strengths']:
                    st.write(f"- {s}")
            with c2:
                st.markdown("**📉 Weak Areas:**")
                for w in interview['weak_areas']:
                    st.write(f"- {w}")
            with c3:
                st.markdown("**💡 Action Plan:**")
                for i in interview['improvements']:
                    st.write(f"- {i}")

render_assistant_sidebar()
_check_env_warnings()

stage = st.session_state["stage"]

if stage == "setup":
    _render_setup()
elif stage == "instructions":
    _render_instructions()
elif stage == "interview":
    _render_interview()
elif stage in ("generating", "evaluating", "summarizing"):
    # These are intermediate states for reroute
    if stage == "generating":
        st.session_state["stage"] = "setup"
        st.rerun()
    elif stage == "evaluating":
        st.session_state["stage"] = "interview"
        st.rerun()
    elif stage == "summarizing":
        st.session_state["stage"] = "summary"
        st.rerun()
elif stage == "summary":
    _render_summary()
elif stage == "dashboard":
    _render_dashboard()
else:
    st.error(f"Unknown stage: {stage}")
    st.session_state["stage"] = "setup"
    st.rerun()
