# AFW Eval Power BI Dashboard

## Open

Double-click **`AFW_Eval_Dashboard.pbip`** (or **`AFW_Eval_Dashboard.Report/definition.pbir`**) or run **`Open_AFW_Dashboard.bat`**.

Data loads from CSV files in `C:\Users\prasa\OneDrive\Desktop\AFW_Eval_Agent_Handoff\workspace\powerbi_export\csv` (absolute paths embedded in model).

## Refresh after new eval runs

1. Run eval agent (menu 1) or `python rewrite_powerbi_exports.py`
2. Rebuild dashboard: `python build_afw_powerbi_dashboard.py`
3. In Power BI Desktop: **Home → Refresh**

## Pages

- Executive Summary
- Persona Drill-Down
- Conversations
- Statistics
- Gold Test Cases
