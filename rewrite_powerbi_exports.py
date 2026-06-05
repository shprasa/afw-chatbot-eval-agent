"""Regenerate workspace Power BI export from all runs in manifest.

Run: python rewrite_powerbi_exports.py
Also runs automatically after each agent evaluation.
"""
from __future__ import annotations

from afw_eval_agent.config import Workspace
from afw_eval_agent.powerbi_export import export_powerbi_data


def main() -> None:
    path = export_powerbi_data(Workspace())
    print(f"Power BI export: {path}")
    print("CSV folder: workspace/powerbi_export/csv/")
    print("Setup guide: workspace/powerbi_export/POWERBI_Setup_Guide.md")


if __name__ == "__main__":
    main()
