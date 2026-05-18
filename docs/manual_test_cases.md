# Comprehensive Manual Test Suite
**Project:** AI Interview Preparation Bot
**Version:** 1.0 (Final Release)

This document contains a structured set of manual test cases designed to evaluate the application under various edge cases, different Job Descriptions, and high-stress scenarios. These tests guarantee the stability and accuracy of the core features.

---

## Category 1: Assistant Coach (Asynchronous Sidebar)

| Test ID | Scenario | Job Description / Setup | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AC-01** | **Basic Concept Explanation** | *React Frontend Developer* | Start interview. Open Assistant Coach sidebar. Type: "Explain the Virtual DOM." | Assistant shows "Thinking..." spinner without freezing the main interview screen. Returns a clear, accurate explanation. | [ ] |
| **AC-02** | **Hint Request on Hard Question** | *Senior DevOps Engineer* | Reach a hard question. Ask the Assistant: "Can you give me a small hint for this question without telling me the answer?" | Assistant reads the current context and provides a subtle hint that guides the user without explicitly revealing the answer. | [ ] |
| **AC-03** | **Clear Chat Confirmation** | *Any* | Send 3 messages to the Assistant. Click the "Clear Chat" button. | A confirmation modal pops up asking to confirm. Clicking "Cancel" retains the chat. Clicking "Confirm" safely wipes the chat history. | [ ] |
| **AC-04** | **Unrelated Off-Topic Prompt** | *Data Analyst* | Ask the Assistant: "Write me a recipe for chocolate cake." | The Assistant (instructed by its system prompt) politely declines and redirects the user back to the interview context. | [ ] |

---

## Category 2: Mock Interview & Core Rules

| Test ID | Scenario | Job Description / Setup | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MI-01** | **Adaptive JIT (Skipping Question)** | *Junior Python Backend* (Set to 10 Questions, Advanced) | Start interview. On Question 1, click "Skip". | App scores the question as a 0. Question 2 is generated slightly easier / more fundamental to adapt to the skip. | [ ] |
| **MI-02** | **Strict Anti-Cheat (Paste Block)** | *Any* | During a question, attempt to paste a copied block of text into the "Your Answer" text area using `Ctrl+V`. | The text area loses focus (blurs) instantly. The user is forced to type manually or use the voice recorder. | [ ] |
| **MI-03** | **Stress Mode Auto-Submit** | *Cybersecurity Analyst* | Toggle "Stress Mode" ON in setup. Start the interview. Do not type anything for 120 seconds. | Timer reaches 0:00. The UI instantly clicks "Evaluate", locks the text area, and evaluates the empty answer (resulting in a 0 score). | [ ] |
| **MI-04** | **Offline Voice Transcription** | *Any* | Click the Microphone icon. Speak a 10-second answer into the microphone. Click stop. | App shows "Transcribing..." and accurately places the text into the "Your Answer" box. | [ ] |
| **MI-05** | **Empty Answer Penalty** | *Any* | Leave the text area completely blank and click "Evaluate". | AI catches the empty answer. Verdict is "Fail". Score is assigned a strict 0. | [ ] |

---

## Category 3: Analytics Dashboard

| Test ID | Scenario | Job Description / Setup | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AD-01** | **Empty Database Check** | *None* | On the Setup screen, click "📊 View Analytics" before doing any interviews. | Dashboard opens and displays an info box: "No interview history found. Complete a mock interview..." No crashes occur. | [ ] |
| **AD-02** | **Accurate Score Logging** | *Java Developer* | Complete a 3-question interview. Score exactly 8, 4, and 0. (Math Average: 4/10 -> 40/100). | Go to Dashboard. The newest interview entry shows a score of exactly `40/100`. | [ ] |
| **AD-03** | **Dropdown Expansion Validation** | *Any completed interview* | On the Dashboard, click the expander for a past interview. | The dropdown expands smoothly, accurately displaying the list of Strengths, Weak Areas, and the Action Plan generated from that session. | [ ] |
| **AD-04** | **Data Persistence** | *Any completed interview* | Close the Streamlit app in terminal (`Ctrl+C`). Restart the app using `streamlit run app.py`. Click View Analytics. | Previous interview history remains intact and loads perfectly from the SQLite database. | [ ] |

---

## Category 4: PDF Generation

| Test ID | Scenario | Job Description / Setup | Steps to Execute | Expected Result | Pass/Fail |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PG-01** | **Standard PDF Generation** | *Marketing Manager* | Complete an entire interview normally. On the summary screen, click "Download PDF Report". | Browser downloads a `.pdf` file. The file opens correctly and is not corrupted. | [ ] |
| **PG-02** | **Content Verification** | *Any* | Open the downloaded PDF. | PDF contains: Overall Score, JD Summary, all Q&As, AI Feedback per question, and the final Improvement Plan. | [ ] |
| **PG-03** | **Skipped Question formatting in PDF** | *Any* | Skip Question 2 during the interview. Complete the rest. Download PDF. | The PDF explicitly shows Question 2 as "Skipped" or "No Answer Provided", with a score of 0 for that specific question. | [ ] |
| **PG-04** | **Non-English/Special Character JD** | *C++ Developer (JD contains symbols like &&, ++, <>)* | Paste a JD filled with coding symbols. Complete interview. Download PDF. | The ReportLab generator safely escapes the XML/HTML characters and the PDF builds successfully without a `ReportLab` crash. | [ ] |
