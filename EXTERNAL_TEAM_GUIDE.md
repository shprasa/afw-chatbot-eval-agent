# AFW Eval Platform — Complete Beginner Guide (External Team)

**Audience:** Angel Flight West partners, UC Davis practicum reviewers, and anyone with **no prior coding experience**.

**GitHub repo (public):** https://github.com/shprasa/afw-chatbot-eval-agent

**What you get:** One website with two pages:
1. **Dashboard** — charts and tables of evaluation results  
2. **Eval Agent** — run new chatbot tests in the browser (no terminal)

Your project lead will share the **Streamlit app URL** (looks like `https://something.streamlit.app`).

---

## Table of contents

1. [Glossary (read this first)](#1-glossary-read-this-first)
2. [What this agent does](#2-what-this-agent-does)
3. [Before you start — requirements checklist](#3-before-you-start--requirements-checklist)
4. [How to open the platform](#4-how-to-open-the-platform)
5. [Dashboard — step-by-step](#5-dashboard--step-by-step)
6. [Eval Agent — step-by-step](#6-eval-agent--step-by-step)
7. [McNemar comparison — step-by-step](#7-mcnemar-comparison--step-by-step)
8. [Save results so everyone sees them](#8-save-results-so-everyone-sees-them)
9. [What gets stored in GitHub](#9-what-gets-stored-in-github)
10. [Optional: run locally (advanced)](#10-optional-run-locally-advanced)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Glossary (read this first)

| Term | Meaning |
|------|---------|
| **Persona** | One fake patient scenario (e.g. F001) with user messages and a **truth** final outcome |
| **Truth** | The correct gold label from the test-case workbook (Eligible, Ineligible, etc.) |
| **Predicted** | What the chatbot said the final outcome should be |
| **Eval run** | One full test of all personas against one model + prompt version |
| **Arm** | A run configuration (e.g. OpenAI v1, Claude v10) |
| **McNemar's test** | Statistical comparison of two runs on the same personas |
| **Dashboard** | Read-only charts fed from saved CSV files in GitHub |
| **Eval Agent** | The tool that calls the live chatbot API and saves results |

---

## 2. What this agent does

The **AFW Screening Chatbot Evaluation Agent** automatically:

1. Reads persona test cases from an Excel workbook (`workspace/datasets/`).
2. Sends only **user messages** to the Angel Flight West chatbot API (labels are **never** sent — no cheating).
3. Collects the chatbot’s predicted eligibility outcome for each persona.
4. Compares **Truth** vs **Predicted** and calculates accuracy.
5. Saves predictions, full conversation transcripts, failure reports, and prompt-improvement notes.
6. Exports clean CSV files for the **Dashboard**.
7. Optionally runs **McNemar's test** between two runs (e.g. OpenAI v1 vs v10).

**Chatbot API endpoints (must be live):**

| Model | URL |
|-------|-----|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

System prompts (v1, v10, etc.) must already be deployed on those servers. The agent only selects a **prompt label** — it does not upload prompt text.

---

## 3. Before you start — requirements checklist

### For most team members (hosted — recommended)

You only need:

- [ ] The **Streamlit app URL** from your project lead  
- [ ] A modern web browser (Chrome, Edge, Firefox)  
- [ ] Internet access  
- [ ] (Only if **you** run evals and save to GitHub) a GitHub token configured by the app owner in Streamlit secrets  

You do **not** need Python, Git, or Power BI installed for viewing the dashboard.

### For whoever runs evaluations on the hosted Eval Agent

The Streamlit app owner must set these **Streamlit Cloud secrets** (one-time setup):

```toml
GITHUB_TOKEN = "a GitHub personal access token with write access to the repo"
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"
```

Without `GITHUB_TOKEN`, you can still **view** the dashboard but cannot **Save to GitHub repo** after a run.

### For local / advanced setup (optional)

| Requirement | Details |
|-------------|---------|
| Python | 3.10 or newer |
| pip packages | `pip install -r requirements.txt` |
| Network | Outbound HTTPS to AFW chatbot URLs above |
| Excel engine | `openpyxl` (included in requirements.txt) |
| OS | Windows, Mac, or Linux |

**Python dependencies** (from `requirements.txt`):

```
pandas, plotly, streamlit, certifi, openpyxl, numpy,
statsmodels, scikit-learn, python-docx
```

---

## 4. How to open the platform

### Step 1 — Open the app

1. Click the link your project lead sent (example format: `https://afw-chatbot-eval-agent.streamlit.app`).
2. The app loads with a **sidebar on the left**.

### Step 2 — Choose your page

At the top of the sidebar you will see navigation:

| Page | Use when you want to… |
|------|------------------------|
| **Dashboard** | View results, charts, errors, conversations |
| **Eval Agent** | Run a new evaluation or McNemar comparison |

Click the page name to switch. **You stay in one browser tab** — no separate installs.

### Step 3 — GitHub repo (optional viewing)

Anyone can browse raw data at:  
https://github.com/shprasa/afw-chatbot-eval-agent  

Key folder: `workspace/powerbi_export/csv/` (feeds the dashboard).

---

## 5. Dashboard — step-by-step

### What the dashboard is

The dashboard is a **live report** built from CSV files in the GitHub repo. When someone saves a new eval to the repo, the dashboard picks up new data (auto-refresh every **20 minutes**, or reload the browser anytime).

### Sidebar controls

| Control | What it does |
|---------|----------------|
| **Auto-refresh (20 min)** | Reloads data from GitHub periodically |
| **Filter arms** | Show only certain eval runs (e.g. Claude v10 only) |
| **Last export** | Timestamp of the latest data export |

### Tabs explained

#### Tab 1 — Run Overview

- **Purpose:** See how each eval arm performed (accuracy bars, comparison table).
- **Use it to:** Answer “Which model/prompt version is winning?”
- **Key numbers:** Persona count (should be **120** per full run), accuracy %, correct count.

#### Tab 2 — Accuracy by Class

- **Purpose:** Recall for each **truth** outcome class (Eligible, Ineligible, Manual Review, Insufficient Information).
- **Use it to:** Find which outcome type the chatbot struggles with.
- **Heatmap:** Rows = truth class, columns = eval arm.

#### Tab 3 — Confusion

- **Purpose:** Truth vs predicted matrix for one arm at a time.
- **Use it to:** See systematic mislabels (e.g. truth Ineligible → predicted Manual Review).

#### Tab 4 — Failure Review

- **Purpose:** List of personas where truth ≠ predicted.
- **Use it to:** Prioritize prompt fixes; open full conversation for any failure.

#### Tab 5 — Conversations

- **Purpose:** Full turn-by-turn transcript for one persona in one run.
- **Use it to:** Read exactly what the user and chatbot said.

#### Tab 6 — McNemar's Test

- **Purpose:** View a statistical comparison between two runs (from Eval Agent).
- **Steps:**
  1. Open this tab.
  2. Use the dropdown **“Comparison (from agent menu 2)”** to pick a saved comparison.
  3. Read paired accuracy, ATE (difference in percentage points), p-value, and 2×2 table.
- **Note:** If the dropdown is empty, someone must run McNemar in **Eval Agent** and **Save to GitHub** first.

#### Tab 7 — User Test Cases

- **Purpose:** View the gold test-case workbook data.
- **Use it to:** See workbook truth columns and, per persona, truth vs predicted from eval runs.

---

## 6. Eval Agent — step-by-step

Go to **Eval Agent** in the sidebar.

### Run a new evaluation

**Step 1 — Open the “Run evaluation” tab**

**Step 2 — Choose settings**

| Field | What to pick |
|-------|----------------|
| **Persona workbook** | Excel file in `workspace/datasets/` (default: 120 test cases) |
| **Model host** | OpenAI or Claude API |
| **Prompt label** | e.g. System Prompt v1 or v10 (must match what’s deployed on the server) |
| **Run label** | Short name you’ll recognize later (e.g. `openai_v10_retest`) |
| **Resume** | Check if a previous run stopped halfway — continues where it left off |
| **Persona limit** | `0` = all personas; use a small number for a quick test |
| **Parallel workers** | Leave at `6` unless told otherwise |

**Step 3 — Click “Start evaluation”**

- A progress panel appears. **Do not close the browser tab.**
- A full 120-persona run can take **30–90+ minutes** depending on API speed.
- When finished, you’ll see “Run saved” with a run ID.

**Step 4 — Save to GitHub (important)**

Click **“Save this eval to GitHub repo”**.

- Wait until you see “Saved N files”.
- Tell your team the dashboard will update within ~20 minutes (or they can reload).

### What happens during an eval (behind the scenes)

For each persona the agent:

1. Opens a new chat session with the chatbot API.  
2. Sends user messages turn by turn (opening, q1–q8).  
3. Records assistant replies.  
4. Reads the session’s final eligibility outcome.  
5. Compares to truth from the workbook.  
6. Writes one row per persona to the predictions CSV.

**Leak guard:** Manual labels and engineered rationales are **never** sent to the API.

---

## 7. McNemar comparison — step-by-step

Use this when you want to know if two runs are **statistically different**.

**Step 1 —** Eval Agent → **“McNemar comparison”** tab  

**Step 2 —** You need **at least two completed runs** in the Saved runs list  

**Step 3 —** Select **Group A** and **Group B** (e.g. OpenAI v1 vs OpenAI v10)  

**Step 4 —** Click **“Run McNemar test”**  

**Step 5 —** Click **“Save McNemar results to GitHub repo”**  

**Step 6 —** Open **Dashboard → McNemar's Test** tab and select your comparison from the dropdown  

---

## 8. Save results so everyone sees them

| Action | Who can do it | Result |
|--------|---------------|--------|
| View Dashboard | Anyone with the Streamlit URL | See current repo data |
| Run eval | Anyone with Eval Agent access | New files in app workspace |
| **Save to GitHub repo** | Requires `GITHUB_TOKEN` in Streamlit secrets | Team dashboard updates |

**Always click Save to GitHub** after:

- A completed evaluation  
- A McNemar comparison  
- Any time you want the external team to see new numbers  

---

## 9. What gets stored in GitHub

```
workspace/
├── datasets/                    Excel persona workbooks
├── runs/
│   ├── manifest.json          Index of all runs
│   └── <run_id>/              One folder per eval
│       ├── *predictions*.csv
│       ├── *transcripts*.jsonl
│       ├── *accuracy*.json
│       └── failure / prompt reports (.md)
├── comparisons/                 McNemar JSON, XLSX, MD
└── powerbi_export/
    └── csv/                     ← Dashboard reads these
        ├── Evaluation_Runs.csv
        ├── Persona_Results.csv
        ├── Turn_Details.csv
        ├── Run_Summary_By_Class.csv
        ├── McNemar_Comparisons.csv
        └── User_Test_Cases.csv
```

### Outcome labels (truth and predicted)

| Label | Meaning |
|-------|---------|
| Eligible | Patient meets criteria |
| Ineligible | Patient does not meet criteria |
| Manual Review | Needs human review |
| Insufficient Information | Not enough info to decide |

### Persona counts

Each run should show **120 personas** for the full benchmark. If a run was resumed, duplicates are removed automatically (keeps the **last** result per `persona_id`).

---

## 10. Optional: run locally (advanced)

Only if you cannot use the hosted app:

```cmd
git clone https://github.com/shprasa/afw-chatbot-eval-agent.git
cd afw-chatbot-eval-agent
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Or CLI-only agent (no browser UI):

```cmd
python run_eval_agent.py
```

Menu options: `1` = run eval, `2` = McNemar, `10` = refresh dashboard export.

Push to GitHub manually:

```cmd
python push_streamlit_dashboard.py
```

---

## 11. Troubleshooting

| Problem | What to do |
|---------|------------|
| Dashboard is empty | Confirm eval was **Saved to GitHub**; reload browser; check repo has `workspace/powerbi_export/csv/Evaluation_Runs.csv` |
| “Save to GitHub” fails | App owner must add `GITHUB_TOKEN` to Streamlit secrets |
| Eval fails immediately | Check chatbot URL is up; try fewer personas (limit = 5) |
| McNemar dropdown empty | Run McNemar in Eval Agent and save to GitHub |
| Wrong persona count (e.g. 122) | Re-save eval after export fix; should show **120** |
| Charts look cut off | Zoom browser to 100%; widen window; charts auto-size on reload |
| Cannot access Streamlit URL | Ask project lead for correct URL and access |

---

## Contact

**UC Davis GSM MSBA — Angel Flight West Demand Management Practicum (2025–2026)**

For access issues: contact your project lead for the Streamlit URL and GitHub invite (if needed).
