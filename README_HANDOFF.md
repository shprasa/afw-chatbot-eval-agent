# AFW Screening Chatbot Evaluation Agent — Technical Reference

> **External team (beginners):** use **[EXTERNAL_TEAM_GUIDE.md](../EXTERNAL_TEAM_GUIDE.md)** first.  
> This file is for developers and operators who need CLI / env-var detail.

Angel Flight West (AFW) live evaluation agent for screening chatbot accuracy.  
Built for the UC Davis Graduate School of Management MSBA Angel Flight West Demand Management practicum.

---

## Hosted platform (primary)

| Component | Access |
|-----------|--------|
| **Dashboard** | Streamlit app → sidebar → **Dashboard** |
| **Eval Agent** | Streamlit app → sidebar → **Eval Agent** |
| **GitHub data** | https://github.com/shprasa/afw-chatbot-eval-agent |

Entry file: `streamlit_app.py`

---

## What this package does

1. **Live eval** — POSTs each persona's user messages to the AFW chatbot API (no manual labels leaked).
2. **Scores** — Compares predicted vs truth final outcome and per-checkpoint (q1–q8).
3. **Reports** — Failure analysis and prompt REMOVE/ADD recommendations.
4. **Dashboard export** — CSV tables under `workspace/powerbi_export/csv/`.
5. **McNemar** — Paired statistical comparison between two runs.

---

## Requirements

- Python 3.10+ (hosted app: managed by Streamlit Cloud)
- Network access to AFW chatbot endpoints
- `pip install -r requirements.txt` (local only)

---

## Quick start — hosted Eval Agent

1. Open Streamlit URL.
2. **Eval Agent** → **Run evaluation**.
3. **Save to GitHub repo** when done.
4. **Dashboard** → view results.

---

## Quick start — CLI agent (optional)

```powershell
python run_eval_agent.py
```

Menu: `1` = eval, `2` = McNemar, `10` = refresh export.

---

## Endpoints

| Arm | URL |
|-----|-----|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

---

## Environment variables (CLI / chatbot_live_eval.py)

| Variable | Purpose |
|----------|---------|
| `CHATBOT_WEB_BASE_URL` | API base URL |
| `CHATBOT_DATASET_XLSX` | Path to persona workbook |
| `CHATBOT_DATASET_SHEET` | Sheet name (default `120_test_cases`) |
| `CHATBOT_OUTPUT_SUFFIX` | Output file suffix |
| `CHATBOT_RESUME` | `1` to skip completed personas |
| `CHATBOT_PARALLEL_WORKERS` | Parallel workers (default 6) |

---

## Outcome encoding

| Code | Label |
|------|-------|
| 0 | ineligible |
| 1 | eligible |
| 2 | insufficient_information |
| 3 | manual_review |

Dashboard displays **Title Case** labels (e.g. Insufficient Information). Use **Truth** (not Gold) in UI.

---

## Leak guard

Only user message columns are sent to the API. Never sent: manual labels, `engineered_for`, labeler notes.

---

## Folder layout

```
workspace/
  datasets/           Excel persona workbooks
  runs/               Per-eval outputs + manifest.json
  comparisons/        McNemar JSON/XLSX/MD
  powerbi_export/     Dashboard CSV + Excel export
  deliverables/       Optional comparison deliverables
```

---

## Push to GitHub

Hosted: **Save to GitHub repo** button in Eval Agent (needs Streamlit `GITHUB_TOKEN`).

Local: `python push_streamlit_dashboard.py`

---

## Contact

UC Davis GSM MSBA Demand Management Practicum Team (2025–2026).
