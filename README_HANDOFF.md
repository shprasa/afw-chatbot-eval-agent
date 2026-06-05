# AFW Chatbot Evaluation Agent — Handoff Package

Angel Flight West (AFW) live evaluation agent for screening chatbot accuracy.
Built for the UC Davis Graduate School of Management MSBA Angel Flight West Demand Management practicum.

## What this package does

1. **Live eval** — POSTs each persona's user messages to the AFW chatbot API (no manual labels leaked).
2. **Scores** — Compares predicted vs gold final outcome and per-checkpoint (q1–q8).
3. **Reports** — Failure analysis and prompt REMOVE/ADD recommendations from API `sessionData` rationales.
4. **Power BI export** — Builds `AFW_Eval_PowerBI_Data.xlsx` from transcript JSONL files.
5. **Comparison workbooks** — Optional DOCX/XLSX deliverables for OpenAI vs Claude and v1 vs v10.

## Requirements

- Python 3.10+
- Windows PowerShell (scripts provided) or set env vars manually on Linux/Mac
- Network access to AFW chatbot endpoints

```bash
pip install -r requirements.txt
```

## Quick start — plug-and-play agent (recommended)

```powershell
cd <handoff_folder>
python run_eval_agent.py
```

Or double-click `Run_Eval_Agent.bat`. Outputs are saved under `workspace/` in this repo
(runs, reports, comparisons). Commit and push after each eval.

## Quick start — PowerShell script (OpenAI v1, 120 personas)

```powershell
cd <handoff_folder>
.\scripts\run_eval_openai_v1.ps1
```

Outputs:
- `artifacts/chatbot_live_predictions_original_style_short_openai.csv`
- `artifacts/chatbot_live_transcripts_original_style_short_openai.jsonl`
- `reports/chatbot_live_accuracy_original_style_short_openai.json`
- `reports/chatbot_live_failure_analysis_original_style_short_openai.md`
- `reports/chatbot_live_prompt_improvements_original_style_short_openai.md`

Resume after interruption:
```powershell
.\scripts\run_eval_openai_v1.ps1 -Resume
```

## Endpoints

| Arm | URL |
|-----|-----|
| OpenAI | https://angel-flight-chatbot-app.azurewebsites.net |
| Claude | https://angel-flight-chatbot-claude.azurewebsites.net |

System prompts v1/v10 must be deployed server-side on the target host.

## Environment variables (reference)

| Variable | Purpose |
|----------|---------|
| `CHATBOT_WEB_BASE_URL` | API base URL |
| `CHATBOT_BACKEND` | `openai` or `claude` (optional) |
| `CHATBOT_DATASET_XLSX` | Path to persona workbook |
| `CHATBOT_DATASET_SHEET` | Sheet name (default `120_test_cases`) |
| `CHATBOT_OUTPUT_SUFFIX` | Output file suffix (e.g. `_original_style_short_openai`) |
| `CHATBOT_OUTPUT_SUFFIX` | Must be unique per run/arm |
| `CHATBOT_RESUME` | `1` to skip personas already in transcript JSONL |
| `CHATBOT_REGEN_REPORTS_ONLY` | `1` to rebuild MD reports from existing CSV/JSONL |
| `CHATBOT_PARALLEL_WORKERS` | Parallel persona workers (default 6) |
| `CHATBOT_ARTIFACTS_DIR` | Override artifacts folder (workspace scratch) |
| `CHATBOT_REPORTS_DIR` | Override reports folder (workspace scratch) |
| `CHATBOT_SSL_VERIFY` | Set `0` if corporate SSL inspection blocks certifi |

## Regenerate reports only (no API calls)

```powershell
$env:CHATBOT_OUTPUT_SUFFIX = "_original_style_short_openai"
$env:CHATBOT_REGEN_REPORTS_ONLY = "1"
python chatbot_live_eval.py
```

Or: `python src/regen_reports.py` (after setting suffix inside script).

## Power BI export

After all four arms have predictions + transcripts:

```powershell
python rewrite_powerbi_exports.py
```

Writes `powerbi_export/AFW_Eval_PowerBI_Data.xlsx` and `AFW_PowerBI_Guide.docx`.

## Outcome encoding

| Code | Label |
|------|-------|
| 0 | ineligible |
| 1 | eligible |
| 2 | insufficient_information |
| 3 | manual_review |

## Leak guard

Only these columns are sent to the API:
- `simulated_user_message`
- `i.` through `viii.` user input message columns

Never sent: `engineered_for`, manual labels, `engineered_for` rationale fields.

## Folder layout

```
AFW_Eval_Agent_Handoff/
  README_HANDOFF.md          (this file)
  AFW_Eval_Agent_README.md   plug-and-play team guide
  requirements.txt
  run_eval_agent.py          interactive wizard entry point
  Run_Eval_Agent.bat         double-click launcher (Windows)
  afw_eval_agent/            wizard, template, McNemar, workspace
  chatbot_live_eval.py       core agent (run from package root)
  rewrite_powerbi_exports.py
  scripts/                   PowerShell runners
  data/                      120-persona gold workbook
  prompts/                   prompt_extract v1/v10 text
  workspace/                 all eval outputs (runs, reports, comparisons) — commit to GitHub
  artifacts/                 legacy script outputs (mirrored into workspace/runs/)
  reports/                   legacy reports (mirrored into workspace/runs/)
  powerbi_export/            dashboard workbook (mirrored into workspace/powerbi_export/)
  deliverables/              comparison XLSX/DOCX (mirrored into workspace/deliverables/)
```

## Contact / lineage

UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management practicum.
Primary module: `chatbot_live_eval.py` (package root).
