# AFW Screening Chatbot Evaluation Agent

This tool runs scripted patient conversations against the Angel Flight West (AFW) screening chatbot, scores the chatbot's answers against your test workbook, and saves reports you can share with your team.

**Created by:** UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum Team (**2025–2026**)

Everything lives in this GitHub repo under `workspace/`. Custom model hosts and prompt labels are saved in `config/agent_registry.json`.

---

## Before you start

You need:

1. **This repo** cloned to your computer  
2. **Python 3.10+** installed  
3. **Internet access** to the AFW chatbot APIs  
4. **A test-case Excel file** that follows the **exact template** (see Step 5)

---

## Step 1 — Get the code

```powershell
git clone https://github.com/shprasa/afw-chatbot-eval-agent.git
cd afw-chatbot-eval-agent
```

---

## Step 2 — Install required packages

```powershell
pip install -r requirements.txt
```

---

## Step 3 — Start the agent

**Windows:** double-click `Run_Eval_Agent.bat`

**Or:**

```powershell
python run_eval_agent.py
```

---

## Step 4 — Choose where files are saved

Press **Enter** to accept the default workspace folder:

```
workspace
```

---

## Step 5 — Run an evaluation

From the main menu, type **1**.

### A) Choose your user persona Excel file

| Option | What it does |
|--------|--------------|
| **1** | Use a workbook already in `workspace/datasets/` |
| **2** | **Upload your own Excel file** — must match the template **exactly** (see below) |
| **3** | Create a blank template to fill in first |

**Strict template rule (option 2):** Your file must use the exact columns and sheet name from:

`workspace/templates/AFW_Eval_Test_Cases_Template.xlsx`

- Sheet name: `test_cases` (or legacy `120_test_cases`)  
- Required columns: `persona_id`, `simulated_user_message`, `i.`–`viii. user input message`, `ix. final eligibility outcome`  
- Do **not** rename or reorder columns  

Uploads that fail validation are **rejected**.

### B) Choose API / model host

Pick a saved host, or choose **Add a new API model host** to register one. New hosts are saved to `config/agent_registry.json` and can be reused on every future run.

Default hosts:

| Key | URL |
|-----|-----|
| OpenAI | `https://angel-flight-chatbot-app.azurewebsites.net` |
| Claude | `https://angel-flight-chatbot-claude.azurewebsites.net` |

### C) Choose prompt version **label**

Pick a saved label, or **Add a new prompt version label**.

**Important:** The system prompt text is changed on the **API backend only**. This agent records a **label** so you can tag which backend prompt was live during the test. You do not edit prompt text here.

Default labels: `System Prompt v1`, `System Prompt v10`

### D) Remaining questions

| Question | What to do |
|----------|------------|
| **Run label** | Short name, e.g. `march_openai_v1` |
| **Resume?** | `n` for fresh run; `y` only if interrupted |
| **Limit personas** | Enter for all, or a number for a test |
| **Parallel workers** | Enter for default `6` |

Outputs save to `workspace/runs/<run_id>/`.

---

## Step 6 — Compare two runs (McNemar)

Main menu → **2**. Pick two completed runs. Reports save to `workspace/comparisons/`.

Four benchmark runs are pre-loaded: `benchmark_openai_v1`, `benchmark_openai_v10`, `benchmark_claude_v1`, `benchmark_claude_v10`.

---

## Step 7 — Add custom models or prompt labels (any time)

| Menu | Action |
|------|--------|
| **7** | Add a new API model host (appended to `config/agent_registry.json`) |
| **8** | Add a new prompt version label (appended to `config/agent_registry.json`) |
| **9** | List all saved models and prompt labels |

Commit `config/agent_registry.json` after adding entries so the team can reuse the same labels.

---

## Step 8 — Save your work to GitHub

```powershell
git add workspace/ config/
git commit -m "Eval run: <label> + registry updates"
git push
```

---

## Main menu

| # | Action |
|---|--------|
| 1 | Run new evaluation |
| 2 | Compare two runs (McNemar) |
| 3 | List saved runs |
| 4 | Create / refresh Excel template |
| 5 | Change workspace folder |
| 6 | Import legacy predictions CSV |
| 7 | Add API model host |
| 8 | Add prompt version label |
| 9 | List saved models and prompt labels |
| 10 | Exit |

---

## Folder layout

```
config/
  agent_registry.json    ← saved model hosts + prompt labels (commit to GitHub)
workspace/
  datasets/              ← persona Excel files (must match template)
  templates/             ← required Excel template
  runs/                  ← predictions, transcripts, reports per run
  comparisons/           ← McNemar outputs
  powerbi_export/
  deliverables/
prompts/                 ← reference prompt text for reports only (not API deploy)
```

---

## More detail

See `README_HANDOFF.md` for environment variables and PowerShell scripts.

---

## About this project

**UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum Team (2025–2026)**
