"""Generate AFW Eval Power BI dashboard (.pbip) using TMSL model.bim + PBIR report."""
from __future__ import annotations

import json
import secrets
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

import pandas as pd

DESK = Path(__file__).resolve().parent
DEFAULT_DATA_ROOT = DESK / "AFW_Eval_Agent_Handoff" / "workspace" / "powerbi_export"
PROJECT_NAME = "AFW_Eval_Dashboard"

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json"
)
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
REPORT_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.0.0/schema.json"

TABLE_CSV = {
    "Evaluation Runs": "Evaluation_Runs.csv",
    "Persona Results": "Persona_Results.csv",
    "Turn Details": "Turn_Details.csv",
    "Run Summary By Class": "Run_Summary_By_Class.csv",
    "User Test Cases": "User_Test_Cases.csv",
    "McNemar Comparisons": "McNemar_Comparisons.csv",
}

NUMERIC_COLS = {
    "Persona Count",
    "Correct Count",
    "Accuracy Pct",
    "Correct Match",
    "Truth Is Eligible",
    "Truth Is Ineligible",
    "Truth Is Manual Review",
    "Truth Is Insufficient Information",
    "Predicted Is Eligible",
    "Predicted Is Ineligible",
    "Predicted Is Manual Review",
    "Predicted Is Insufficient Information",
    "Turn Number",
    "Checkpoint Correct",
    "Personas In Class",
    "Correct In Class",
    "Recall Pct",
    "truth_is_eligible",
    "truth_is_ineligible",
    "truth_is_manual_review",
    "truth_is_insufficient_information",
    "engineered_for_code",
    "Paired Personas",
    "Accuracy A Pct",
    "Accuracy B Pct",
    "Ate Percentage Points",
    "A Only Correct",
    "B Only Correct",
    "Mcnemar P Value",
    "Significant At 0 05",
    "Run Count",
}


def _uid() -> str:
    return secrets.token_hex(12)


def _guid() -> str:
    return str(uuid.uuid4())


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _pbi_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "\\\\")


def _infer_dtype(col: str) -> str:
    if col in NUMERIC_COLS or col.endswith(" Code") or col.endswith(" Pct"):
        return "double"
    return "string"


def _csv_m_expression(csv_path: Path) -> list[str]:
    p = _pbi_path(csv_path)
    return [
        "let",
        f'    Source = Csv.Document(File.Contents("{p}"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])',
        "in",
        '    #"Promoted Headers"',
    ]


def _tmsl_column(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "dataType": _infer_dtype(name),
        "sourceColumn": name,
        "summarizeBy": "none",
        "annotations": [{"name": "SummarizationSetBy", "value": "Automatic"}],
    }


def _tmsl_table(name: str, csv_path: Path, columns: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "columns": [_tmsl_column(c) for c in columns],
        "partitions": [
            {
                "name": name,
                "mode": "import",
                "source": {"type": "m", "expression": _csv_m_expression(csv_path)},
            }
        ],
        "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
    }


def _build_model_bim(data_root: Path) -> dict[str, Any]:
    csv_dir = data_root / "csv"
    tables: list[dict[str, Any]] = []

    mcnemar_cols = [
        "Comparison File",
        "Group A",
        "Group B",
        "Paired Personas",
        "Accuracy A Pct",
        "Accuracy B Pct",
        "Ate Percentage Points",
        "A Only Correct",
        "B Only Correct",
        "Mcnemar P Value",
        "Significant At 0 05",
    ]

    for table_name, csv_name in TABLE_CSV.items():
        csv_path = csv_dir / csv_name
        if not csv_path.is_file() and table_name == "McNemar Comparisons":
            csv_path.write_text(
                "Comparison File,Group A,Group B,Paired Personas,Accuracy A Pct,Accuracy B Pct,"
                "Ate Percentage Points,A Only Correct,B Only Correct,Mcnemar P Value,Significant At 0 05\n"
                "No comparisons yet,Run menu 2 in eval agent to compare two runs,,,,,,,,\n",
                encoding="utf-8-sig",
            )
        if csv_path.is_file():
            df = pd.read_csv(csv_path, nrows=0)
            columns = list(df.columns)
        elif table_name == "McNemar Comparisons":
            columns = mcnemar_cols
        else:
            columns = ["Note"]
        if not columns:
            columns = ["Note"]
        tables.append(_tmsl_table(table_name, csv_path, columns))

    tables.append(
        {
            "name": "_Metrics",
            "columns": [
                {
                    "name": "Placeholder",
                    "dataType": "string",
                    "isHidden": True,
                    "sourceColumn": "Placeholder",
                }
            ],
            "measures": [
                {
                    "name": "Avg Accuracy Pct",
                    "expression": "AVERAGE('Evaluation Runs'[Accuracy Pct])",
                    "formatString": "0.0",
                },
                {
                    "name": "Total Runs",
                    "expression": "COUNTROWS('Evaluation Runs')",
                    "formatString": "0",
                },
                {
                    "name": "Persona Correct Rate",
                    "expression": (
                        "DIVIDE("
                        "COUNTROWS(FILTER('Persona Results', 'Persona Results'[Correct Match] = 1)),"
                        "COUNTROWS('Persona Results')"
                        ")"
                    ),
                    "formatString": "0.0%;-0.0%;0.0%",
                },
            ],
            "partitions": [
                {
                    "name": "_Metrics",
                    "mode": "import",
                    "source": {
                        "type": "calculated",
                        "expression": 'DATATABLE("Placeholder", STRING, {{" "}})',
                    },
                }
            ],
        }
    )

    relationships = [
        {
            "name": _guid(),
            "fromTable": "Persona Results",
            "fromColumn": "Run ID",
            "toTable": "Evaluation Runs",
            "toColumn": "Run ID",
        },
        {
            "name": _guid(),
            "fromTable": "Persona Results",
            "fromColumn": "Persona ID",
            "toTable": "User Test Cases",
            "toColumn": "persona_id",
        },
        {
            "name": _guid(),
            "fromTable": "Turn Details",
            "fromColumn": "Run ID",
            "toTable": "Evaluation Runs",
            "toColumn": "Run ID",
        },
        {
            "name": _guid(),
            "fromTable": "Turn Details",
            "fromColumn": "Persona ID",
            "toTable": "User Test Cases",
            "toColumn": "persona_id",
        },
        {
            "name": _guid(),
            "fromTable": "Run Summary By Class",
            "fromColumn": "Run ID",
            "toTable": "Evaluation Runs",
            "toColumn": "Run ID",
        },
    ]

    return {
        "name": PROJECT_NAME,
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True,
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "sourceQueryCulture": "en-US",
            "tables": tables,
            "relationships": relationships,
            "annotations": [
                {"name": "PBI_QueryOrder", "value": json.dumps(list(TABLE_CSV.keys()))},
                {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
            ],
        },
    }


def _build_semantic_model(model_dir: Path, data_root: Path) -> None:
    _write_json(model_dir / "definition.pbism", {"version": "1.0", "settings": {}})
    _write_json(model_dir / "model.bim", _build_model_bim(data_root))
    _write_json(
        model_dir / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "SemanticModel", "displayName": PROJECT_NAME},
            "config": {"version": "2.0", "logicalId": _guid()},
        },
    )


def _col_field(table: str, column: str) -> dict[str, Any]:
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": column,
            }
        },
        "queryRef": f"{table}.{column}",
        "nativeQueryRef": column,
    }


def _measure_field(table: str, measure: str) -> dict[str, Any]:
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": table}},
                "Property": measure,
            }
        },
        "queryRef": f"{table}.{measure}",
        "nativeQueryRef": measure,
    }


def _visual_container(
    visual_type: str,
    x: int,
    y: int,
    w: int,
    h: int,
    query_state: dict[str, Any],
    z: int = 0,
) -> dict[str, Any]:
    return {
        "$schema": VISUAL_SCHEMA,
        "name": _uid(),
        "position": {"x": x, "y": y, "z": z, "height": h, "width": w, "tabOrder": z},
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_state},
            "drillFilterOtherVisuals": True,
        },
    }


def _card_visual(table: str, measure: str, x: int, y: int, w: int = 280, h: int = 140) -> dict[str, Any]:
    return _visual_container("card", x, y, w, h, {"Values": {"projections": [_measure_field(table, measure)]}})


def _bar_visual(table: str, category: str, value_col: str, x: int, y: int, w: int, h: int) -> dict[str, Any]:
    return _visual_container(
        "barChart",
        x,
        y,
        w,
        h,
        {
            "Category": {"projections": [{**_col_field(table, category), "active": True}]},
            "Y": {"projections": [_col_field(table, value_col)]},
        },
    )


def _table_visual(table: str, columns: list[str], x: int, y: int, w: int, h: int) -> dict[str, Any]:
    return _visual_container(
        "tableEx",
        x,
        y,
        w,
        h,
        {"Values": {"projections": [_col_field(table, c) for c in columns]}},
    )


def _slicer_visual(table: str, column: str, x: int, y: int, w: int = 260, h: int = 100) -> dict[str, Any]:
    return _visual_container(
        "slicer",
        x,
        y,
        w,
        h,
        {"Values": {"projections": [{**_col_field(table, column), "active": True}]}},
    )


def _matrix_visual(
    rows_table: str,
    rows_col: str,
    cols_table: str,
    cols_col: str,
    val_table: str,
    val_col: str,
    x: int,
    y: int,
    w: int,
    h: int,
) -> dict[str, Any]:
    return _visual_container(
        "pivotTable",
        x,
        y,
        w,
        h,
        {
            "Rows": {"projections": [{**_col_field(rows_table, rows_col), "active": True}]},
            "Columns": {"projections": [{**_col_field(cols_table, cols_col), "active": True}]},
            "Values": {"projections": [_col_field(val_table, val_col)]},
        },
    )


def _page_background() -> dict[str, Any]:
    return {
        "background": [
            {
                "properties": {
                    "color": {
                        "solid": {
                            "color": {
                                "expr": {
                                    "ThemeDataColor": {"ColorId": 0, "Percent": -0.1}
                                }
                            }
                        }
                    },
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}},
                }
            }
        ]
    }


def _write_page(report_def: Path, display_name: str, visuals: list[dict[str, Any]]) -> str:
    # Page folder name MUST match page.json "name" exactly or Desktop silently drops the page.
    page_id = _uid()
    page_dir = report_def / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        page_dir / "page.json",
        {
            "$schema": PAGE_SCHEMA,
            "name": page_id,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
            "objects": _page_background(),
        },
    )
    for visual in visuals:
        vdir = page_dir / "visuals" / f"{visual['name']}.Visual"
        _write_json(vdir / "visual.json", visual)
    return page_id


def _write_base_theme(report_dir: Path) -> None:
    theme_path = (
        report_dir
        / "StaticResources"
        / "SharedResources"
        / "BaseThemes"
        / "CY24SU10.json"
    )
    if theme_path.is_file():
        return
    theme_url = (
        "https://raw.githubusercontent.com/data-goblin/power-bi-agentic-development/"
        "main/plugins/pbip/skills/pbir-format/examples/K201-MonthSlicer.Report/"
        "StaticResources/SharedResources/BaseThemes/CY24SU10.json"
    )
    try:
        import urllib.request

        theme_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(theme_url, timeout=30) as resp:
            theme_path.write_bytes(resp.read())
    except Exception:
        _write_json(
            theme_path,
            {
                "name": "CY24SU10",
                "foreground": "#252423",
                "background": "#FFFFFF",
                "tableAccent": "#118DFF",
            },
        )


def _build_report(report_dir: Path) -> None:
    report_def = report_dir / "definition"
    report_def.mkdir(parents=True, exist_ok=True)
    _write_base_theme(report_dir)

    _write_json(
        report_dir / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../AFW_Eval_Dashboard.SemanticModel"}},
        },
    )
    _write_json(
        report_dir / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "Report", "displayName": f"{PROJECT_NAME} Report"},
            "config": {"version": "2.0", "logicalId": _guid()},
        },
    )
    _write_json(
        report_def / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "2.0.0",
        },
    )
    _write_json(
        report_def / "report.json",
        {
            "$schema": REPORT_SCHEMA,
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU10",
                    "type": "SharedResources",
                    "reportVersionAtImport": {
                        "visual": "1.8.95",
                        "report": "2.0.95",
                        "page": "1.3.95",
                    },
                }
            },
            "resourcePackages": [
                {
                    "name": "SharedResources",
                    "type": "SharedResources",
                    "items": [
                        {
                            "name": "CY24SU10",
                            "path": "BaseThemes/CY24SU10.json",
                            "type": "BaseTheme",
                        }
                    ],
                }
            ],
            "settings": {
                "useStylableVisualContainerHeader": True,
                "defaultDrillFilterOtherVisuals": True,
            },
        },
    )

    pages: list[tuple[str, list[dict[str, Any]]]] = [
        (
            "Executive Summary",
            [
                _card_visual("_Metrics", "Avg Accuracy Pct", 24, 24),
                _card_visual("_Metrics", "Total Runs", 320, 24),
                _card_visual("_Metrics", "Persona Correct Rate", 616, 24),
                _bar_visual("Evaluation Runs", "Display Name", "Accuracy Pct", 24, 180, 620, 500),
                _table_visual(
                    "Evaluation Runs",
                    [
                        "Display Name",
                        "Model Display",
                        "Prompt Label",
                        "Persona Count",
                        "Correct Count",
                        "Accuracy Pct",
                        "Created UTC",
                    ],
                    660,
                    180,
                    596,
                    500,
                ),
            ],
        ),
        (
            "Persona Drill-Down",
            [
                _slicer_visual("Evaluation Runs", "Display Name", 24, 24, 300, 110),
                _slicer_visual("Persona Results", "Persona ID", 340, 24, 220, 110),
                _table_visual(
                    "Persona Results",
                    ["Display Name", "Persona ID", "Truth Label", "Predicted Label", "Correct Match"],
                    24,
                    150,
                    1232,
                    260,
                ),
                _matrix_visual(
                    "Run Summary By Class",
                    "Outcome Class",
                    "Run Summary By Class",
                    "Display Name",
                    "Run Summary By Class",
                    "Recall Pct",
                    24,
                    430,
                    1232,
                    260,
                ),
            ],
        ),
        (
            "Conversations",
            [
                _slicer_visual("Turn Details", "Persona ID", 24, 24, 240, 110),
                _slicer_visual("Turn Details", "Display Name", 280, 24, 420, 110),
                _table_visual(
                    "Turn Details",
                    [
                        "Display Name",
                        "Persona ID",
                        "Turn Number",
                        "Question",
                        "User Message",
                        "Assistant Response",
                        "Checkpoint Correct",
                    ],
                    24,
                    150,
                    1232,
                    540,
                ),
            ],
        ),
        (
            "Statistics",
            [
                _table_visual(
                    "McNemar Comparisons",
                    [
                        "Comparison File",
                        "Group A",
                        "Group B",
                        "Accuracy A Pct",
                        "Accuracy B Pct",
                        "Mcnemar P Value",
                        "Significant At 0 05",
                    ],
                    24,
                    24,
                    1232,
                    660,
                ),
            ],
        ),
        (
            "Gold Test Cases",
            [
                _slicer_visual("User Test Cases", "persona_id", 24, 24, 200, 110),
                _table_visual(
                    "User Test Cases",
                    [
                        "persona_id",
                        "engineered_for",
                        "simulated_user_message",
                        "ix. final eligibility outcome",
                        "ix. manual label",
                        "labeler notes",
                    ],
                    24,
                    150,
                    1232,
                    540,
                ),
            ],
        ),
    ]

    page_order = [_write_page(report_def, display, visuals) for display, visuals in pages]
    _write_json(
        report_def / "pages" / "pages.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
            "pageOrder": page_order,
            "activePageName": page_order[0],
        },
    )


def _refresh_export_data(data_root: Path) -> None:
    rewrite = DESK / "rewrite_powerbi_exports.py"
    if rewrite.is_file():
        subprocess.run([sys.executable, str(rewrite)], check=False, cwd=str(DESK))


def build_dashboard(data_root: Path | None = None, output_dir: Path | None = None) -> Path:
    data_root = (data_root or DEFAULT_DATA_ROOT).resolve()
    _refresh_export_data(data_root)

    csv_dir = data_root / "csv"
    if not csv_dir.is_dir() or not any(csv_dir.glob("*.csv")):
        raise FileNotFoundError(f"Missing CSV export folder: {csv_dir}")

    out = (output_dir or data_root).resolve()
    model_dir = out / f"{PROJECT_NAME}.SemanticModel"
    report_dir = out / f"{PROJECT_NAME}.Report"

    for d in (model_dir, report_dir):
        if d.exists():
            shutil.rmtree(d)

    _build_semantic_model(model_dir, data_root)
    _build_report(report_dir)

    pbip_path = out / f"{PROJECT_NAME}.pbip"
    # PBIP schema only allows a report artifact; the semantic model is linked
    # from definition.pbir via datasetReference.byPath.
    _write_json(
        pbip_path,
        {
            "version": "1.0",
            "artifacts": [
                {"report": {"path": f"{PROJECT_NAME}.Report"}},
            ],
            "settings": {"enableAutoRecovery": True},
        },
    )

    _write_text(
        out / "DASHBOARD_README.md",
        f"""# AFW Eval Power BI Dashboard

## Open

Double-click **`{PROJECT_NAME}.pbip`** (or **`{PROJECT_NAME}.Report/definition.pbir`**) or run **`Open_AFW_Dashboard.bat`**.

Data loads from CSV files in `{csv_dir}` (absolute paths embedded in model).

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
""",
    )
    return pbip_path


def _launch_power_bi(pbip_path: Path) -> None:
    pbi = Path(r"C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe")
    if pbi.is_file():
        subprocess.Popen([str(pbi), str(pbip_path)], shell=False)


def main() -> None:
    data_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_DATA_ROOT
    pbip = build_dashboard(data_root=data_root)
    print(f"Built dashboard: {pbip}")
    print(f"CSV data folder: {data_root / 'csv'}")
    _launch_power_bi(pbip)
    print("Launched Power BI Desktop.")


if __name__ == "__main__":
    main()
