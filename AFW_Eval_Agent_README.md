# AFW Chatbot Evaluation Agent — team guide

All agent files and outputs live in **this GitHub repo** under `workspace/`.

## Quick start

```powershell
git clone <repo-url>
cd afw-chatbot-eval-agent
pip install -r requirements.txt
python run_eval_agent.py
```

Default workspace: `workspace/` (press Enter).

## After each eval

```powershell
git add workspace/
git commit -m "Eval run: <label>"
git push
```

## What's in workspace/

- `runs/` — predictions, transcripts, accuracy JSON, failure + prompt reports  
- `comparisons/` — McNemar outputs  
- `datasets/` — test case workbooks  
- `powerbi_export/` — Power BI data workbook  
- `deliverables/` — comparison DOCX/XLSX  

Four benchmark runs are pre-loaded for McNemar (OpenAI v1/v10, Claude v1/v10).

See **README.md** for full technical handoff.
