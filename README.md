# AFW Screening Chatbot Evaluation Agent

This tool runs scripted patient conversations against the Angel Flight West (AFW) screening chatbot, scores the chatbot's answers against your test workbook, and saves reports you can share with your team.

Everything lives in this GitHub repo under the `workspace/` folder.

---

## Before you start

You need:

1. **This repo** cloned or downloaded to your computer  
2. **Python 3.10+** installed  
3. **Internet access** to the AFW chatbot APIs  
4. **A test-case Excel file** (use the template in `workspace/templates/` or the bundled file in `workspace/datasets/`)

---

## Step 1 — Get the code

```powershell
git clone https://github.com/shprasa/afw-chatbot-eval-agent.git
cd afw-chatbot-eval-agent
```

---

## Step 2 — Install required packages

Open PowerShell or Terminal in the repo folder and run:

```powershell
pip install -r requirements.txt
```

---

## Step 3 — Start the agent

**Windows:** double-click `Run_Eval_Agent.bat`

**Or run:**

```powershell
python run_eval_agent.py
```

A text menu will appear in your terminal.

---

## Step 4 — Choose where files are saved

On first launch, the agent asks for a **workspace folder**.

Press **Enter** to accept the default:

```
workspace
```

That folder is inside this repo. All runs, reports, and comparisons are saved there.

---

## Step 5 — Run an evaluation

From the main menu, type **1** and press Enter.

The agent will ask you a few questions. Here is what to pick:

| Question | What to do |
|----------|------------|
| **Test cases file** | Choose **1** to use a file already in `workspace/datasets/`, or **3** to create a blank Excel template first |
| **API / model host** | **1** = OpenAI host, **2** = Claude host |
| **System prompt** | **1** = Prompt v1, **2** = Prompt v10 |
| **Run label** | Type a short name, e.g. `march_openai_v1` |
| **Resume?** | Type **n** for a fresh run (type **y** only if a previous run was interrupted) |
| **Limit personas** | Press Enter to run all personas (or type a number for a small test) |
| **Parallel workers** | Press Enter to accept **6** |

The agent will POST each persona's user messages to the chatbot API. **Manual labels are never sent** — only the user-input message columns from your Excel file.

When the run finishes, outputs are saved to:

```
workspace/runs/<run_id>/
```

Each run folder includes:

- Predictions spreadsheet (`.csv`)
- Full conversation log (`.jsonl`)
- Accuracy summary (`.json`)
- Failure analysis report (`.md`)
- Prompt improvement suggestions (`.md`)

---

## Step 6 — Compare two runs (McNemar test)

From the main menu, type **2** and press Enter.

The agent lists completed runs. Pick **two** (for example, OpenAI v1 vs Claude v1).

Reports are saved to:

```
workspace/comparisons/
```

You get an Excel file, Word document, and summary markdown with paired accuracy and p-value.

**Four benchmark runs are already loaded** so you can compare immediately:

| Run | What it is |
|-----|------------|
| `benchmark_openai_v1` | OpenAI host + Prompt v1 |
| `benchmark_openai_v10` | OpenAI host + Prompt v10 |
| `benchmark_claude_v1` | Claude host + Prompt v1 |
| `benchmark_claude_v10` | Claude host + Prompt v10 |

---

## Step 7 — Save your work to GitHub

After a new run or comparison:

```powershell
git add workspace/
git commit -m "Add eval run: <your run label>"
git push
```

---

## Main menu reference

| Option | What it does |
|--------|--------------|
| **1** | Run a new evaluation |
| **2** | Compare two runs (McNemar) |
| **3** | List saved runs |
| **4** | Create or refresh the Excel test-case template |
| **5** | Change workspace folder |
| **6** | Import an older predictions CSV into the run list |
| **7** | Exit |

---

## Test-case Excel format

Use sheet name **`test_cases`** (or legacy **`120_test_cases`**).

**Required columns:**

- `persona_id` — unique ID per row (e.g. F001)  
- `simulated_user_message` — opening message  
- `i.` through `viii. user input message` — eight screening answers  
- `ix. final eligibility outcome` — correct final label for scoring  

Download or copy the template from `workspace/templates/AFW_Eval_Test_Cases_Template.xlsx`.

---

## API hosts

| Model | URL |
|-------|-----|
| **OpenAI** | `https://angel-flight-chatbot-app.azurewebsites.net` |
| **Claude** | `https://angel-flight-chatbot-claude.azurewebsites.net` |

Both use `POST /api/chat` and `POST /api/reset-session`.

---

## Where everything is stored

```
workspace/
├── datasets/          ← your test-case Excel files
├── templates/         ← Excel template
├── runs/              ← one folder per evaluation run
├── comparisons/       ← McNemar comparison outputs
├── powerbi_export/    ← Power BI workbook
└── deliverables/      ← comparison reports (DOCX / XLSX)
```

---

## More detail

See `README_HANDOFF.md` for environment variables, PowerShell scripts, and advanced options.

---

## About this project

**UC Davis Graduate School of Management MSBA** — Angel Flight West Demand Management practicum (2025–2026).
