# AFW Eval Platform — Complete Beginner Guide

**Audience:** Angel Flight West partners, UC Davis practicum reviewers, and anyone with **no prior coding experience**.

---

## Where to go (bookmark these)

| Tool | Direct link | What it is for |
|------|-------------|----------------|
| **Eval Agent** | **https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent** | Run live chatbot tests and McNemar comparisons |
| **Dashboard** | **https://afw-chatbot-eval-agent.streamlit.app** | View charts, errors, conversations, and comparison results |

No install. No terminal. Open the link in Chrome, Edge, or Firefox.

---

## Table of contents

1. [Glossary](#1-glossary)
2. [What the Eval Agent does](#2-what-the-eval-agent-does)
3. [Before you start](#3-before-you-start)
4. [Eval Agent — step-by-step](#4-eval-agent--step-by-step)
5. [McNemar comparison — step-by-step](#5-mcnemar-comparison--step-by-step)
6. [Save results for the team](#6-save-results-for-the-team)
7. [Dashboard — step-by-step](#7-dashboard--step-by-step)
8. [What gets saved after a run](#8-what-gets-saved-after-a-run)
9. [Optional: run locally (advanced)](#9-optional-run-locally-advanced)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Glossary

| Term | Meaning |
|------|---------|
| **Persona** | One test patient scenario (e.g. F001) with user messages and a **truth** final outcome |
| **Truth** | The correct label from the test-case workbook (Eligible, Ineligible, etc.) |
| **Predicted** | What the chatbot said the final outcome should be |
| **Eval run** | One full test of all personas against one model + prompt version |
| **Arm** | A run configuration (e.g. OpenAI v1, Claude v10) |
| **McNemar's test** | Statistical comparison of two runs on the same personas |
| **Eval Agent** | The tool that calls the live chatbot API and saves results |
| **Dashboard** | Read-only charts built from saved evaluation data |

---

## 2. What the Eval Agent does

The **AFW Screening Chatbot Evaluation Agent** automatically:

1. Reads persona test cases from an Excel workbook.
2. Sends only **user messages** to the Angel Flight West chatbot API (truth labels are **never** sent).
3. Collects the chatbot’s predicted eligibility outcome for each persona.
4. Compares **Truth** vs **Predicted** and calculates accuracy.
5. Saves predictions, full conversation transcripts, failure reports, and prompt-improvement notes.
6. Exports clean CSV files that feed the **Dashboard**.
7. Optionally runs **McNemar's test** between two runs (e.g. OpenAI v1 vs v10).

**Chatbot API endpoints (must be live):**

| Model | URL |
|-------|-----|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

System prompts (v1, v10, etc.) must already be deployed on those servers. The agent only selects a **prompt label** — it does not upload prompt text.

---

## 3. Before you start

### Hosted use (recommended)

You only need:

- [ ] A web browser (Chrome, Edge, or Firefox)
- [ ] Internet access
- [ ] The **Eval Agent** link: https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent
- [ ] The **Dashboard** link: https://afw-chatbot-eval-agent.streamlit.app

You do **not** need Python, Git, or any desktop software to view results or run hosted evaluations.

### If you run evaluations

After each completed eval or McNemar run, click **Save results** so the team dashboard updates. If saving fails, contact the AFW platform administrator.

### Optional local setup (advanced)

| Requirement | Details |
|-------------|---------|
| Python | 3.10 or newer |
| Packages | `pip install -r requirements.txt` |
| Network | Outbound HTTPS to the AFW chatbot URLs above |

**Dependencies:** `pandas`, `plotly`, `streamlit`, `certifi`, `openpyxl`, `numpy`, `statsmodels`, `scikit-learn`, `python-docx`

---

## 4. Eval Agent — step-by-step

**Open:** https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent

### Run a new evaluation

**Step 1 —** Open the **Run evaluation** tab.

**Step 2 — Choose settings**

| Field | What to pick |
|-------|----------------|
| **Persona workbook** | Default 120 test cases |
| **Model host** | OpenAI or Claude API |
| **Prompt label** | e.g. System Prompt v1 or v10 (must match what’s deployed on the server) |
| **Run label** | Short name you’ll recognize later (e.g. `openai_v10_retest`) |
| **Resume** | Check if a previous run stopped halfway |
| **Persona limit** | `0` = all personas; use a small number for a quick test |
| **Parallel workers** | Leave at `6` unless told otherwise |

**Step 3 —** Click **Start evaluation**.

- A progress panel appears. **Do not close the browser tab.**
- A full 120-persona run can take **30–90+ minutes** depending on API speed.
- When finished, you’ll see “Run saved” with a run ID.

**Step 4 —** Click **Save results** (or **Save to GitHub repo**).

- Wait until you see a success message.
- The dashboard will update within ~20 minutes, or sooner if you reload the Dashboard page.

### What happens during an eval

For each persona the agent:

1. Opens a new chat session with the chatbot API.
2. Sends user messages turn by turn (opening, q1–q8).
3. Records assistant replies.
4. Reads the session’s final eligibility outcome.
5. Compares to truth from the workbook.
6. Writes one row per persona to the predictions file.

**Leak guard:** Manual labels and engineered rationales are **never** sent to the API.

---

## 5. McNemar comparison — step-by-step

**Open:** https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent → **McNemar comparison** tab

Use this when you want to know if two runs are **statistically different**.

1. You need **at least two completed runs** in the Saved runs list.
2. Select **Group A** and **Group B** (e.g. OpenAI v1 vs OpenAI v10).
3. Click **Run McNemar test**.
4. Click **Save results**.
5. Open the **Dashboard** → **McNemar's Test** tab and select your comparison from the dropdown.

---

## 6. Save results for the team

| Action | Link | Result |
|--------|------|--------|
| Run eval | https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent | New run data in the platform |
| View dashboard | https://afw-chatbot-eval-agent.streamlit.app | Charts and tables for the team |

**Always click Save results** after:

- A completed evaluation
- A McNemar comparison
- Any time you want the team to see new numbers

---

## 7. Dashboard — step-by-step

**Open:** https://afw-chatbot-eval-agent.streamlit.app

### What the dashboard is

The dashboard is a **live report** built from saved evaluation data. When someone saves a new eval, the dashboard picks up new data (auto-refresh every **20 minutes**, or reload the browser anytime).

### Sidebar controls

| Control | What it does |
|---------|----------------|
| **Auto-refresh (20 min)** | Reloads data periodically |
| **Filter arms** | Show only certain eval runs (e.g. Claude v10 only) |
| **Last export** | Timestamp of the latest data export |

### Tabs explained

#### Run Overview

- **Purpose:** See how each eval arm performed (accuracy bars, comparison table).
- **Use it to:** Answer “Which model/prompt version is winning?”
- **Key numbers:** Persona count (should be **120** per full run), accuracy %, correct count.

#### Accuracy by Class

- **Purpose:** Recall for each **truth** outcome class (Eligible, Ineligible, Manual Review, Insufficient Information).
- **Use it to:** Find which outcome type the chatbot struggles with.

#### Confusion

- **Purpose:** Truth vs predicted matrix for one arm at a time.
- **Use it to:** See systematic mislabels (e.g. truth Ineligible → predicted Manual Review).

#### Failure Review

- **Purpose:** List of personas where truth ≠ predicted.
- **Use it to:** Prioritize prompt fixes; open full conversation for any failure.

#### Conversations

- **Purpose:** Full turn-by-turn transcript for one persona in one run.

#### McNemar's Test

- **Purpose:** View a statistical comparison between two runs.
- Pick a saved comparison from the dropdown. If empty, run McNemar in the **Eval Agent** and save first.

#### User Test Cases

- **Purpose:** View test-case workbook data and truth vs predicted per persona.

---

## 8. What gets saved after a run

Each evaluation produces:

- Predictions CSV (one row per persona)
- Full conversation transcripts
- Accuracy summary
- Failure analysis and prompt-improvement notes
- Dashboard CSV tables (Evaluation Runs, Persona Results, Turn Details, etc.)

### Outcome labels

| Label | Meaning |
|-------|---------|
| Eligible | Patient meets criteria |
| Ineligible | Patient does not meet criteria |
| Manual Review | Needs human review |
| Insufficient Information | Not enough info to decide |

### Persona counts

Each full benchmark run should show **120 personas**. If a run was resumed, duplicates are removed automatically (keeps the **last** result per persona).

---

## 9. Optional: run locally (advanced)

```cmd
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open:

- Dashboard: http://localhost:8501
- Eval Agent: use the sidebar to switch pages

CLI-only (no browser UI):

```cmd
python run_eval_agent.py
```

Menu: `1` = run eval, `2` = McNemar, `10` = refresh dashboard export.

---

## 10. Troubleshooting

| Problem | What to do |
|---------|------------|
| Dashboard is empty | Confirm an eval was **saved** after running; reload https://afw-chatbot-eval-agent.streamlit.app |
| Save results fails | Contact the AFW platform administrator |
| Eval fails immediately | Check chatbot URL is up; try fewer personas (limit = 5) |
| McNemar dropdown empty | Run McNemar in the Eval Agent and save |
| Wrong persona count (e.g. 122) | Re-save eval; should show **120** |
| Charts look cut off | Zoom browser to 100%; widen window; reload |
| Cannot open links | Confirm you are using the URLs in the table at the top of this guide |

---

## Contact

**UC Davis GSM MSBA — Angel Flight West Demand Management Practicum (2025–2026)**
