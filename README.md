# AFW Screening Chatbot Evaluation Platform

Angel Flight West (AFW) · UC Davis GSM MSBA Practicum · **Public repo:** https://github.com/shprasa/afw-chatbot-eval-agent

---

## Start here (external team)

**New to this project?** Read the full beginner guide:

**[EXTERNAL_TEAM_GUIDE.md](EXTERNAL_TEAM_GUIDE.md)** — step-by-step instructions, dashboard tour, eval agent walkthrough, requirements, troubleshooting.

---

## What is this?

Two tools in **one hosted website** (Streamlit — no terminal required):

| Page | URL in app sidebar | Purpose |
|------|-------------------|---------|
| **Dashboard** | Click **Dashboard** | View charts, errors, conversations, McNemar results |
| **Eval Agent** | Click **Eval Agent** | Run live chatbot evaluations and statistical comparisons |

Your project lead shares one link: `https://<your-app>.streamlit.app`

---

## 5-minute quick start

### View results only (most team members)

1. Open the Streamlit URL from your project lead.
2. Click **Dashboard** in the sidebar.
3. Use the tabs (Run Overview, Accuracy by Class, Confusion, etc.).
4. Optionally filter which eval **arms** appear in the sidebar.

No install. No GitHub account required to **view** (public repo + public app).

### Run a new evaluation (operators)

1. Open the Streamlit URL → **Eval Agent**.
2. Tab **Run evaluation** → pick workbook, model, prompt label.
3. Click **Start evaluation** → wait for completion (can take up to ~90 min for 120 personas).
4. Click **Save to GitHub repo** (requires app owner to configure token — see below).
5. Switch to **Dashboard** → data updates within 20 minutes or on browser reload.

### Compare two runs (McNemar)

1. **Eval Agent** → **McNemar comparison** tab.
2. Pick Group A and Group B → **Run McNemar test**.
3. **Save McNemar results to GitHub repo**.
4. **Dashboard** → **McNemar's Test** tab → select comparison from dropdown.

---

## Pre-run requirements

### Hosted (recommended)

| Requirement | Details |
|-------------|---------|
| Browser | Chrome, Edge, or Firefox |
| Internet | Access to Streamlit app + AFW chatbot APIs |
| Streamlit URL | From project lead |
| GitHub token | Only for **saving** runs — configured in Streamlit secrets by app owner |

### Chatbot APIs (must be online)

| Arm | Base URL |
|-----|----------|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

Prompt versions (v1, v10) must be deployed on the server before testing.

### Streamlit secrets (app owner — one time)

In [share.streamlit.io](https://share.streamlit.io) → your app → **Settings → Secrets**:

```toml
GITHUB_TOKEN = "ghp_xxxxxxxx"
GITHUB_OWNER = "shprasa"
GITHUB_REPO = "afw-chatbot-eval-agent"
GITHUB_BRANCH = "main"
```

Deploy settings: **Main file** = `streamlit_app.py`, **Repo** = `afw-chatbot-eval-agent`.

### Local setup (optional / advanced)

```
Python 3.10+
pip install -r requirements.txt
```

Dependencies: `pandas`, `plotly`, `streamlit`, `openpyxl`, `numpy`, `statsmodels`, `scikit-learn`, `python-docx`, `certifi`.

```cmd
streamlit run streamlit_app.py
```

---

## What the agent does (plain English)

1. Loads persona test cases from Excel (`workspace/datasets/`).
2. Sends **only user messages** to the AFW chatbot (truth labels are never sent).
3. Records predicted vs **truth** final outcome per persona.
4. Saves predictions, transcripts, accuracy JSON, failure analysis, prompt suggestions.
5. Exports dashboard CSVs to `workspace/powerbi_export/csv/`.
6. Supports **McNemar's test** between any two completed runs.

See [README_HANDOFF.md](README_HANDOFF.md) for technical reference (env vars, folder layout, encoding).

---

## Dashboard tabs (summary)

| Tab | What you see |
|-----|----------------|
| **Run Overview** | Accuracy by arm, comparison table (dynamic — no static executive summary) |
| **Accuracy by Class** | Recall heatmap by truth outcome class |
| **Confusion** | Truth × predicted matrix per arm |
| **Failure Review** | Wrong predictions + conversation drill-down |
| **Conversations** | Full transcripts |
| **McNemar's Test** | Pick a saved comparison; stats + 2×2 breakdown |
| **User Test Cases** | Gold workbook + truth vs predicted per persona |

Auto-refresh: every **20 minutes** (toggle in sidebar).

---

## Repo layout (what matters)

```
afw-chatbot-eval-agent/
├── streamlit_app.py           ← Hosted app entry (Dashboard + Eval Agent)
├── afw_eval_dashboard/        ← Dashboard code
├── afw_eval_agent_ui/         ← Eval Agent web UI
├── afw_eval_agent/            ← Core agent logic
├── chatbot_live_eval.py       ← Live API runner
├── run_eval_agent.py          ← CLI agent (optional)
├── requirements.txt
├── EXTERNAL_TEAM_GUIDE.md     ← Full beginner guide
├── DEPLOY_TEAM_DASHBOARD.md   ← Deploy instructions for app owner
└── workspace/
    ├── datasets/              Persona Excel files
    ├── runs/                  Eval outputs per run
    ├── comparisons/           McNemar results
    └── powerbi_export/csv/    Dashboard data (auto-generated)
```

---

## Saving data for the team

After each eval or McNemar run, click **Save to GitHub repo** in the Eval Agent.

This uploads runs, comparisons, and dashboard CSVs so everyone with the Streamlit link sees updated charts.

Manual push from a developer machine:

```cmd
python push_streamlit_dashboard.py
```

---

## Documentation index

| Document | Audience |
|----------|----------|
| **[EXTERNAL_TEAM_GUIDE.md](EXTERNAL_TEAM_GUIDE.md)** | External team — complete step-by-step |
| [DEPLOY_TEAM_DASHBOARD.md](DEPLOY_TEAM_DASHBOARD.md) | Who deploys Streamlit Cloud |
| [STREAMLIT_DEPLOY_NOW.md](STREAMLIT_DEPLOY_NOW.md) | Quick deploy checklist |
| [README_HANDOFF.md](README_HANDOFF.md) | Technical reference (CLI, env vars) |
| [workspace/powerbi_export/POWERBI_Setup_Guide.md](workspace/powerbi_export/POWERBI_Setup_Guide.md) | Optional Power BI Desktop |

---

## Troubleshooting (short)

| Issue | Fix |
|-------|-----|
| Empty dashboard | Save eval to GitHub; reload browser |
| Save button fails | Add `GITHUB_TOKEN` to Streamlit secrets |
| McNemar tab empty | Run McNemar in Eval Agent + save |
| Persona count not 120 | Data uses deduplicated predictions; re-export after save |

Full FAQ: [EXTERNAL_TEAM_GUIDE.md § Troubleshooting](EXTERNAL_TEAM_GUIDE.md#11-troubleshooting)

---

## Contact

UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum (2025–2026).
