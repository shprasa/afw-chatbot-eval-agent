# AFW Screening Chatbot Evaluation Agent

## What is this?

This program tests the Angel Flight West (AFW) screening chatbot. It:

1. Reads fake patient conversations from an **Excel file** on your computer  
2. Sends those messages to the live AFW chatbot website (one message at a time)  
3. Compares the chatbot's answers to the correct answers in your Excel file  
4. Saves reports in a folder called `workspace`

You do **not** need to know how to code. You only need to copy/paste a few commands and answer simple questions in the terminal.

**Created by:** UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum Team (**2025–2026**)

---

# PART A — ONE-TIME SETUP (do this once on your computer)

## A1. Install Python (if you do not already have it)

1. Open your web browser.  
2. Go to: https://www.python.org/downloads/  
3. Click the yellow **Download Python** button.  
4. Run the installer.  
5. **Important:** On the first screen, check the box that says **"Add python.exe to PATH"**.  
6. Click **Install Now** and wait until it finishes.

**Check that it worked:**

1. Press the **Windows key** on your keyboard.  
2. Type `PowerShell` and press **Enter**. A blue window opens.  
3. Type this and press **Enter:**

```powershell
python --version
```

4. You should see something like `Python 3.12.x`. If you see an error, restart your computer and try again.

---

## A2. Download this project to your computer

**Option 1 — Download as ZIP (easiest if you do not use git):**

1. Open: https://github.com/shprasa/afw-chatbot-eval-agent  
2. Click the green **Code** button.  
3. Click **Download ZIP**.  
4. Unzip the file (right-click → **Extract All**).  
5. Remember the folder location, for example:  
   `C:\Users\YourName\Downloads\afw-chatbot-eval-agent`

**Option 2 — Clone with git:**

```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/shprasa/afw-chatbot-eval-agent.git
cd afw-chatbot-eval-agent
```

---

## A3. Install the Python packages this tool needs

1. Open **PowerShell**.  
2. Go into the project folder. Replace the path with **your** folder path:

```powershell
cd C:\Users\YourName\Downloads\afw-chatbot-eval-agent
```

3. Run this command (copy the whole line, paste into PowerShell, press **Enter**):

```powershell
pip install -r requirements.txt
```

4. Wait until it finishes. You should see no red error text at the end.

**You only need to do A1–A3 once** (unless you move to a new computer).

---

# PART B — EVERY TIME YOU WANT TO RUN THE AGENT

## B1. Open the project folder

1. Open **PowerShell**.  
2. Type `cd` followed by the path to your project folder, then press **Enter**:

```powershell
cd C:\Users\YourName\Downloads\afw-chatbot-eval-agent
```

*(Use your real path from step A2.)*

---

## B2. Start the agent

**Easiest way on Windows:**

1. Open **File Explorer**.  
2. Go to your project folder.  
3. Double-click **`Run_Eval_Agent.bat`**.  
4. A black window opens. That is the agent.

**Or** in PowerShell (same folder as B1):

```powershell
python run_eval_agent.py
```

You should see:

```
=== AFW Screening Chatbot Evaluation Agent ===
```

and then a list of menu numbers.

---

## B3. First question: where to save files

The agent asks:

```
Workspace folder (repo workspace/) [C:\...\afw-chatbot-eval-agent\workspace]:
```

**Just press Enter.** Do not type anything. This accepts the default `workspace` folder.

You should see: `Workspace ready: ...`

---

# PART C — RUN YOUR FIRST EVALUATION (most common task)

You are now at the **Main menu**. Follow these steps exactly.

## C1. Start a new evaluation

The menu shows:

```
  1. Run new evaluation
  2. Compare two runs (McNemar)
  ...
```

1. Type **`1`**  
2. Press **Enter**

---

## C2. Pick your Excel test file

You will see:

```
User persona test cases (Excel):
  1. Use a file already in workspace/datasets/
  2. Upload your own Excel file (must match template EXACTLY)
  3. Create a blank template to fill in first
Choice [1]:
```

### If this is your first time — use the built-in 120 test cases:

1. Type **`1`**  
2. Press **Enter**  
3. If only one file exists, the agent uses it automatically.  
4. If several files are listed, type the number next to the file you want, then press **Enter**.

### If you want to use YOUR OWN Excel file:

1. Type **`2`**  
2. Press **Enter**  
3. The agent shows template rules. Read them.  
4. When asked for the file path, paste the full path to your `.xlsx` file, for example:  
   `C:\Users\YourName\Documents\my_test_cases.xlsx`  
5. Press **Enter**  
6. If your file does not match the template **exactly**, the agent will stop and tell you what is wrong. Fix the Excel file and try again.

**Your Excel file MUST match this template:**

- Open this file in Excel: `workspace\templates\AFW_Eval_Test_Cases_Template.xlsx`  
- Sheet name must be: `test_cases`  
- Column names must be spelled exactly as in the template (do not rename columns)

### If you need to build a new Excel file from scratch:

1. Type **`3`**  
2. Press **Enter**  
3. The agent creates a blank template.  
4. Open `workspace\templates\AFW_Eval_Test_Cases_Template.xlsx` in Excel, fill in your rows, save.  
5. Start again from **C1** and choose option **2** to upload your filled-in file.

---

## C3. Pick which chatbot server to test

You will see something like:

```
Which API / model host?
  1. OpenAI (angel-flight-chatbot-app)
  2. Claude (angel-flight-chatbot-claude)
  3. Add a new API model host ...
Enter number:
```

**For a standard OpenAI test:**

1. Type **`1`**  
2. Press **Enter**

**For a standard Claude test:**

1. Type **`2`**  
2. Press **Enter**

---

## C4. Pick a prompt version label

You will see:

```
Note: The system prompt is deployed on the API backend only.
You are selecting a LABEL to tag this run — not editing prompt text.

Which prompt version label?
  1. System Prompt v1
  2. System Prompt v10
  3. Add a new prompt version label ...
Enter number:
```

**This does NOT change the prompt.** It only records which prompt version was live on the server when you ran the test.

**For most v1 tests:**

1. Type **`1`**  
2. Press **Enter**

**For v10 tests:**

1. Type **`2`**  
2. Press **Enter**

---

## C5. Answer the remaining questions

The agent will ask one question at a time. Here is what to type for a normal full run:

| Question you see | What to type | Then press |
|------------------|--------------|------------|
| `Run label (short name for reports) [eval_run]:` | A short name, e.g. `my_first_test` | Enter |
| `Resume incomplete run? (y/N) [n]:` | `n` | Enter |
| `Limit personas (blank = all):` | *(leave blank)* | Enter |
| `Parallel workers [6]:` | *(leave blank)* | Enter |

---

## C6. Wait for the run to finish

- The agent sends messages to the chatbot over the internet. This can take **several minutes** (longer for more personas).  
- **Do not close the window** while it is running.  
- When done, you will see: `Run complete. Saved to workspace:`

---

## C7. Find your results on your computer

1. Open **File Explorer**.  
2. Go to your project folder.  
3. Open the `workspace` folder.  
4. Open the `runs` folder.  
5. Open the **newest folder** (sorted by date).  

Inside that folder you will find:

| File | What it is |
|------|------------|
| `chatbot_live_predictions...csv` | Spreadsheet of chatbot answers vs correct answers |
| `chatbot_live_transcripts...jsonl` | Full conversation log |
| `chatbot_live_accuracy...json` | Accuracy score summary |
| `chatbot_live_failure_analysis...md` | Report of mistakes (open in Notepad) |
| `chatbot_live_prompt_improvements...md` | Suggestions for prompt changes (open in Notepad) |

---

# PART D — COMPARE TWO RUNS (McNemar test)

Use this when you have **two finished runs** and want to see if they are statistically different.

1. Start the agent (Part B).  
2. At the main menu, type **`2`** and press **Enter**.  
3. You will see a numbered list of past runs. Four are already loaded from prior benchmark tests.  
4. `Select Group A [1]:` — type **`1`** (or the number of your first run) and press **Enter**.  
5. `Select Group B [2]:` — type **`2`** (or the number of your second run) and press **Enter**.  
6. Results are saved in: `workspace\comparisons\`  
7. Open the `.xlsx` file in Excel to read the comparison.

---

# PART E — ADD A NEW CHATBOT SERVER OR PROMPT LABEL (optional)

Do this when AFW adds a new API host or a new prompt version label.

## Add a new API server (menu 7)

1. Start the agent.  
2. At the main menu, type **`7`** and press **Enter**.  
3. Type a display name (example: `New staging host`).  
4. Type the base URL (example: `https://my-new-host.azurewebsites.net`).  
5. Type `openai` or `claude`.  
6. The agent saves it to `config\agent_registry.json`.  
7. Next time you run an evaluation, your new server appears in the list.

## Add a new prompt label (menu 8)

1. At the main menu, type **`8`** and press **Enter**.  
2. Type a label (example: `System Prompt v12 — April deploy`).  
3. Add optional notes if you want.  
4. Saved to `config\agent_registry.json`.  
5. **Reminder:** This only saves a label. The actual prompt text is changed by the engineering team on the server — not in this tool.

## See everything saved (menu 9)

Type **`9`** at the main menu to list all servers and prompt labels.

---

# PART F — POWER BI DASHBOARD (connects to this repo)

The agent **automatically updates** clean Power BI files after every evaluation run.

**Data location:**

```
workspace/powerbi_export/
  AFW_PowerBI_Data.xlsx     ← open this in Power BI Desktop
  csv/                      ← or connect Power BI to this folder
  POWERBI_Setup_Guide.md    ← full dashboard build instructions
```

**What is inside the Excel file (clean labels, no underscores):**

| Sheet | Contents |
|-------|----------|
| User Test Cases | Original Excel columns preserved exactly from the source file |
| Evaluation Runs | One row per agent run (model, prompt label, accuracy) |
| Persona Results | Truth vs predicted labels per persona (Eligible, not eligible) |
| Turn Details | Full conversation text per turn |
| Run Summary By Class | Recall by outcome class |
| McNemar Comparisons | Statistical comparisons between runs |

**To refresh Power BI after new agent runs:**

1. `git pull` (get latest repo data)  
2. Open Power BI Desktop → **Refresh**  
3. Or run agent menu **10** to regenerate export manually  

**Full step-by-step** to build the dashboard (relationships, visuals, pages):  
read `workspace/powerbi_export/POWERBI_Setup_Guide.md`

---

# PART G — SAVE YOUR WORK BACK TO GITHUB (optional)

If you use git and want to upload new runs for your team:

```powershell
cd C:\Users\YourName\Downloads\afw-chatbot-eval-agent
git add workspace/ config/
git commit -m "Added evaluation run and refreshed Power BI data"
git push
```

If you downloaded the ZIP and do not use git, you can share the `workspace` folder by email, SharePoint, or any file-sharing method.

---

# QUICK REFERENCE — Main menu

| Type this | What happens |
|-----------|--------------|
| **1** | Run a new evaluation (Parts C) |
| **2** | Compare two runs (Part D) |
| **3** | List past runs |
| **4** | Create a fresh Excel template |
| **5** | Change save folder (usually not needed) |
| **6** | Import an old results CSV |
| **7** | Add a new API server |
| **8** | Add a new prompt label |
| **9** | List saved servers and labels |
| **10** | Refresh Power BI export now |
| **11** | Exit |

---

# TROUBLESHOOTING

| Problem | What to try |
|---------|-------------|
| `'python' is not recognized` | Reinstall Python with **Add to PATH** checked (step A1) |
| `'pip' is not recognized` | Try `python -m pip install -r requirements.txt` |
| Excel upload rejected | Open `workspace\templates\AFW_Eval_Test_Cases_Template.xlsx` and match columns exactly |
| Run stopped halfway | Start again (menu 1), same choices, but answer `y` to **Resume** |
| Window closes immediately | Open PowerShell first, `cd` to the folder, then run `python run_eval_agent.py` |
| No runs listed for McNemar | Complete at least two evaluations first (Part C) |

---

# WHERE FILES LIVE

```
afw-chatbot-eval-agent/
├── Run_Eval_Agent.bat     ← double-click to start (Windows)
├── run_eval_agent.py      ← or run this with Python
├── config/
│   └── agent_registry.json   ← saved servers + prompt labels
└── workspace/
    ├── datasets/          ← Excel test files
    ├── templates/         ← REQUIRED Excel template (copy this format)
    ├── runs/              ← your results (one folder per run)
    └── comparisons/       ← McNemar comparison outputs
```

---

# MORE TECHNICAL DETAIL

See `README_HANDOFF.md` for environment variables and advanced scripts.

---

**UC Davis Graduate School of Management MSBA — Angel Flight West Demand Management Practicum Team (2025–2026)**
