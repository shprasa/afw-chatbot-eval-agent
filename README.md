# AFW Screening Chatbot Evaluation Platform

Angel Flight West (AFW) · UC Davis GSM MSBA Practicum

---

## Where to go

| Tool | Direct link |
|------|-------------|
| **Eval Agent** (run tests) | **https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent** |
| **Dashboard** (view results) | **https://afw-chatbot-eval-agent.streamlit.app** |

**New to this project?** Read **[AFW_TEAM_GUIDE.md](AFW_TEAM_GUIDE.md)** — full step-by-step instructions.

---

## What is this?

Two tools hosted on Streamlit — no terminal required:

| Tool | Link | Purpose |
|------|------|---------|
| **Eval Agent** | https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent | Run live chatbot evaluations and McNemar comparisons |
| **Dashboard** | https://afw-chatbot-eval-agent.streamlit.app | View charts, errors, conversations, and comparison results |

---

## Quick start

### Run a new evaluation

1. Open **https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent**
2. Tab **Run evaluation** → pick workbook, model, prompt label
3. Click **Start evaluation** → wait for completion (up to ~90 min for 120 personas)
4. Click **Save results**
5. Open **https://afw-chatbot-eval-agent.streamlit.app** — data updates within 20 minutes or on reload

### Compare two runs (McNemar)

1. **https://afw-chatbot-eval-agent.streamlit.app/Eval_Agent** → **McNemar comparison** tab
2. Pick Group A and Group B → **Run McNemar test**
3. **Save results**
4. **https://afw-chatbot-eval-agent.streamlit.app** → **McNemar's Test** tab → select comparison

### View results only

1. Open **https://afw-chatbot-eval-agent.streamlit.app**
2. Use the tabs: Run Overview, Accuracy by Class, Confusion, Failure Review, Conversations, McNemar's Test, User Test Cases

---

## Pre-run requirements

| Requirement | Details |
|-------------|---------|
| Browser | Chrome, Edge, or Firefox |
| Internet | Access to the Streamlit app and AFW chatbot APIs |

### Chatbot APIs (must be online)

| Arm | Base URL |
|-----|----------|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

Prompt versions (v1, v10) must be deployed on the server before testing.

### Optional local setup

```
Python 3.10+
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## What the Eval Agent does

1. Loads persona test cases from Excel.
2. Sends **only user messages** to the AFW chatbot (truth labels are never sent).
3. Records predicted vs **truth** final outcome per persona.
4. Saves predictions, transcripts, accuracy, failure analysis, and prompt suggestions.
5. Exports dashboard CSV tables after each run.
6. Supports **McNemar's test** between two completed runs.

See [README_HANDOFF.md](README_HANDOFF.md) for technical reference (CLI, env vars).

---

## Dashboard tabs

| Tab | What you see |
|-----|----------------|
| **Run Overview** | Accuracy by arm, comparison table |
| **Accuracy by Class** | Recall heatmap by truth outcome class |
| **Confusion** | Truth × predicted matrix per arm |
| **Failure Review** | Wrong predictions + conversation drill-down |
| **Conversations** | Full transcripts |
| **McNemar's Test** | Saved comparison stats + 2×2 breakdown |
| **User Test Cases** | Workbook truth vs predicted per persona |

Auto-refresh: every **20 minutes** (toggle in sidebar).

---

## Documentation

| Document | Audience |
|----------|----------|
| **[AFW_TEAM_GUIDE.md](AFW_TEAM_GUIDE.md)** | AFW team — complete step-by-step |
| [README_HANDOFF.md](README_HANDOFF.md) | Technical reference (CLI, env vars) |
| [DEPLOY_TEAM_DASHBOARD.md](DEPLOY_TEAM_DASHBOARD.md) | Quick links and team workflow |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Empty dashboard | Save eval results; reload https://afw-chatbot-eval-agent.streamlit.app |
| Save results fails | Contact the AFW platform administrator |
| McNemar tab empty | Run McNemar in Eval Agent and save |
| Persona count not 120 | Re-save eval; export deduplicates by persona |

Full FAQ: [AFW_TEAM_GUIDE.md](AFW_TEAM_GUIDE.md)

---

## Contact

UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum (2025–2026).
