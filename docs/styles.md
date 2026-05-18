```md
# styles.md — UI Styling & Design System
**Product:** AI Interview Preparation Bot (Hybrid)  
**Platform:** Streamlit Web App  
**Version:** 1.0  
**Last Updated:** 2026-05-08

---

## 1) Design Goals
1. **Professional & calm:** should feel like an interview platform, not a toy.
2. **High readability:** optimized for long text (JDs, answers, feedback).
3. **Clear hierarchy:** users always know the current step (Setup → Interview → Summary).
4. **Fast scanning:** scores, verdicts, and action items are visually prominent.
5. **Consistent tokens:** use design tokens (colors, spacing, type scale) rather than random styling.

---

## 2) Brand & Theme

### 2.1 Theme Name
**Modern Professional (Indigo)**

### 2.2 Color Tokens
Use these as the single source of truth.

#### Core
- `--color-primary`: **#4F46E5** (Indigo 600)
- `--color-primary-dark`: **#312E81** (Indigo 900)
- `--color-bg`: **#F8FAFC** (Slate 50)
- `--color-surface`: **#FFFFFF** (White)
- `--color-text`: **#1E293B** (Slate 800)
- `--color-text-muted`: **#64748B** (Slate 500)
- `--color-border`: **#E2E8F0** (Slate 200)

#### Semantic
- `--color-success`: **#10B981** (Emerald 500)
- `--color-warning`: **#F59E0B** (Amber 500)
- `--color-error`: **#EF4444** (Red 500)
- `--color-info`: **#2563EB** (Blue 600)

#### Verdict Badge (recommended mapping)
- **Poor:** `--color-error`
- **Fair:** `--color-warning`
- **Good:** `--color-info`
- **Excellent:** `--color-success`

#### Data Viz (optional)
- `--color-chart-1`: #4F46E5
- `--color-chart-2`: #06B6D4
- `--color-chart-3`: #22C55E
- `--color-chart-4`: #F59E0B
- `--color-chart-5`: #EF4444

---

## 3) Typography System

### 3.1 Font Family
**Primary:** Inter (Google Fonts)  
**Fallback stack:** `Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial`

### 3.2 Type Scale
- **H1 (App Title):** 32px / 40px, 700
- **H2 (Section Title):** 24px / 32px, 600
- **H3 (Card Title):** 18px / 26px, 600
- **Body (default):** 16px / 26px, 400
- **Small / Caption:** 13–14px / 20px, 400
- **Monospace blocks:** system monospace (for ideal answer / JSON debug only)

### 3.3 Typography Rules
- Avoid ALL CAPS headings.
- Keep line length ~70–90 characters for long feedback.
- Use bullet lists for feedback, missing concepts, and improvement plan.

---

## 4) Spacing, Layout, and Grid

### 4.1 Layout Constraints
- **Max content width:** 1100px (centered)
- **Primary layout:**
  - Main content: interview flow cards
  - Sidebar: Assistant Bot + Settings (collapsible recommended)

### 4.2 Spacing Tokens (8px grid)
- `--space-1`: 4px
- `--space-2`: 8px
- `--space-3`: 12px
- `--space-4`: 16px
- `--space-5`: 24px
- `--space-6`: 32px
- `--space-7`: 40px
- `--space-8`: 48px

### 4.3 Card & Section Spacing
- Card padding: 16–24px
- Card gap: 16px
- Section gap: 24–32px

---

## 5) Components & Visual Specs

### 5.1 Buttons
**Primary Button**
- Background: `--color-primary`
- Text: white
- Use for: *Generate Interview*, *Evaluate Answer*, *Download PDF*

**Secondary Button**
- Outline or neutral background
- Use for: *Skip*, *Restart*, *Back*

**Destructive Button**
- Use for: *Clear Session*
- Color: `--color-error`

**Rules**
- One primary action per view.
- Disable primary buttons when prerequisites are missing (e.g., no JD).

### 5.2 Inputs
**JD Text Area**
- Large, comfortable height (min 200–280px)
- Helper text: max words, example JD snippet

**Knowledge Level**
- Radio buttons: Basic / Medium / Advanced
- Tooltip: what each level changes

**Question Count**
- Segmented control or select box: 8,10,12,15,20

### 5.3 Badges (Category + Verdict)
**Category Badge**
- Technical: Indigo tint
- Behavioral: Blue tint
- HR: Slate tint
- Situational: Cyan tint
- System Design: Purple tint

**Verdict Badge**
- Pill shape, bold text
- Color mapping as defined in section 2.2

### 5.4 Progress
- Progress bar in Primary color
- Text: “Question X of Y”
- Show completion at end (100%)

### 5.5 Feedback Blocks
Use consistent sections:
- **Score + Verdict (top)**
- **What was good**
- **What’s missing**
- **How to improve**
- **Ideal answer (collapsible expander)**

### 5.6 Assistant Bot (Sidebar)
- Simple chat layout
- Provide quick prompts:
  - “Explain this question”
  - “Give a strong sample answer”
  - “What concepts should I mention?”
- Button: “Use current question as context”

---

## 6) Page-Level Styling Guidelines

### 6.1 Setup Page (JD → Level → Count → Generate)
- One hero title + short subtitle
- JD card first, then controls card
- Provider selection placed in “Advanced / Settings” expander

### 6.2 Interview Page
- Top: progress + question card
- Middle: answer input
- Right/Below: evaluation panel (appears after Evaluate)
- Keep actions fixed and predictable: Evaluate, Skip, Next

### 6.3 Summary & Report Page
- Show:
  - Overall score (0–100) large
  - Readiness label (badge)
  - Strengths & weaknesses (2-column layout if possible)
  - Improvement plan (top 5 actions)
- Download PDF button prominent

---

## 7) Accessibility Requirements (Practical)
- Contrast ratio: minimum AA for text (aim for 4.5:1)
- Don’t rely only on color for verdict (include label text)
- Ensure focus states on inputs/buttons (Streamlit defaults generally OK)
- Use clear error messages near the relevant input

---

## 8) Streamlit Theming & CSS Implementation

### 8.1 `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#4F46E5"
backgroundColor = "#F8FAFC"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1E293B"
font = "sans serif"
```

### 8.2 Add Inter Font + Optional Custom CSS (in `app.py`)
```python
import streamlit as st

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Optional: tighten container width */
  .block-container { max-width: 1100px; padding-top: 1.5rem; }

  /* Optional: card-like containers (use with st.container + custom class if needed) */
  .soft-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px;
  }
</style>
""", unsafe_allow_html=True)
```

> Note: Streamlit’s DOM class names can change. Prefer Streamlit-native layout (`st.container`, `st.columns`, `st.expander`) and only use CSS for light enhancements.

---

## 9) PDF Visual Style (Report)
Even though PDF is generated via ReportLab, keep it consistent with UI.

### 9.1 PDF Colors
- Header bar: `#4F46E5`
- Body text: `#1E293B`
- Subheadings: `#312E81`
- Borders/lines: `#E2E8F0`

### 9.2 PDF Typography
- Title: 18–22pt, bold
- Section headings: 12–14pt, semibold
- Body: 10–11pt
- Spacing: generous margins, clear separation between Q/A blocks

### 9.3 PDF Layout Sections
1. Cover header (App name + date)
2. JD Summary (short)
3. Overall Score + Readiness
4. Questions table/list (Question → Answer → Score → Key feedback)
5. Improvement Plan (top 5)
6. Footer (page number)

---

## 10) UI Copy Guidelines (Tone)
- Tone: supportive, direct, professional
- Avoid harsh wording; prefer actionable guidance
- Examples:
  - Instead of “Wrong answer” → “Missing key concepts: …”
  - Instead of “Bad” → “Needs improvement”

---

## 11) Component Checklist (Build Reference)
- [ ] Theme configured via `config.toml`
- [ ] Inter font loaded
- [ ] Setup screen uses clear cards and helper text
- [ ] Interview view shows progress + category badge
- [ ] Evaluation view uses consistent sections and verdict badge
- [ ] Summary view highlights overall score and next steps
- [ ] Assistant bot always accessible in sidebar
- [ ] PDF matches the same brand colors and typography

---
```