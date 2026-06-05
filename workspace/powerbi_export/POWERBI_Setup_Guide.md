# Power BI — Connect to GitHub Data (Auto-Refresh)

## Where the data lives in this repo

```
workspace/powerbi_export/
  AFW_PowerBI_Data.xlsx      ← main workbook (8 clean sheets)
  csv/                       ← same tables as CSV (for folder connector)
  refresh_manifest.json      ← last update timestamp
```

**The agent updates these files automatically after every evaluation run.**

After each run, commit and push:

```powershell
git add workspace/powerbi_export/
git commit -m "Refresh Power BI data"
git push
```

---

## Step 1 — Sync this repo to your computer

1. Clone: `git clone https://github.com/shprasa/afw-chatbot-eval-agent.git`
2. Or use **GitHub Desktop** → Clone repository
3. Before opening Power BI, run `git pull` to get the latest data

---

## Step 2 — Open Power BI Desktop and connect

### Option A — Excel workbook (recommended)

1. Open **Power BI Desktop**
2. **Home** → **Get data** → **Excel**
3. Browse to: `afw-chatbot-eval-agent\workspace\powerbi_export\AFW_PowerBI_Data.xlsx`
4. Select these tables (check all):
   - User Test Cases
   - Evaluation Runs
   - Persona Results
   - Turn Details
   - Run Summary By Class
   - McNemar Comparisons
5. Click **Load**

### Option B — CSV folder (updates when CSV files change)

1. **Get data** → **Text/CSV**
2. Choose **Folder** and select: `workspace\powerbi_export\csv`
3. Click **Transform Data** → combine files if prompted → **Load**

---

## Step 3 — Set up relationships (Model view)

Drag to create relationships:

| From (Table) | Column | To (Table) | Column |
|--------------|--------|------------|--------|
| Persona Results | Run ID | Evaluation Runs | Run ID |
| Persona Results | Persona ID | User Test Cases | Persona ID |
| Turn Details | Run ID | Evaluation Runs | Run ID |
| Turn Details | Persona ID | User Test Cases | Persona ID |
| Run Summary By Class | Run ID | Evaluation Runs | Run ID |

---

## Step 4 — Build starter dashboard pages

### Page 1 — Executive Summary
- Card: **Accuracy Pct** (average from Evaluation Runs)
- Bar chart: **Display Name** vs **Accuracy Pct**
- Table: Evaluation Runs (all columns)

### Page 2 — Persona Drill-Down
- Slicer: **Display Name** (from Evaluation Runs)
- Slicer: **Persona ID**
- Table: Persona Results — Truth Label, Predicted Label, Correct Match
- Matrix: **Outcome Class** (rows) × **Display Name** (columns) — values: **Recall Pct**

### Page 3 — Conversations
- Slicer: Persona ID
- Table: Turn Details — Question, User Message, Assistant Response

### Page 4 — Statistics
- Table: McNemar Comparisons

### Page 5 — Gold Test Cases
- Table: User Test Cases (all original columns preserved)

---

## Step 5 — Refresh after new agent runs

1. Team member runs evaluation → agent auto-updates `workspace/powerbi_export/`
2. `git pull` on your computer
3. Power BI Desktop → **Home** → **Refresh**
4. Or publish to Power BI Service with **Gateway** for scheduled refresh

---

## Column naming rules

- No underscores in display names (uses spaces and Title Case)
- Outcome labels: Eligible, Ineligible, Insufficient Information, Manual Review
- User Test Cases sheet keeps **original Excel column names** from the source file
