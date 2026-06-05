"""Excel test-case template generation and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

TEMPLATE_SHEET_NAMES = ("test_cases", "120_test_cases")

TEMPLATE_STRICT_NOTICE = """
STRICT TEMPLATE REQUIRED
Your Excel file must follow the exact column layout in:
  workspace/templates/AFW_Eval_Test_Cases_Template.xlsx
Sheet name must be: test_cases (or legacy 120_test_cases).
Do not rename columns. Uploads that fail validation cannot be used.
""".strip()

REQUIRED_COLUMNS = ("persona_id", "simulated_user_message", "ix. final eligibility outcome")
USER_INPUT_COLS = [
    f"{roman}. user input message"
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")
]
MANUAL_LABEL_COLS = [
    f"{roman}. manual label"
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")
]
OPTIONAL_COLUMNS = (
    "engineered_for",
    "engineered_for_code",
    "labeler notes",
    "ix. manual label",
    *MANUAL_LABEL_COLS,
    "truth_is_eligible",
    "truth_is_ineligible",
    "truth_is_manual_review",
    "truth_is_insufficient_information",
)

README_ROWS: list[dict[str, str]] = [
    {
        "topic": "Overview",
        "detail": (
            "Upload this workbook to run live chatbot evaluations. "
            "Only user-input message columns are POSTed to /api/chat — "
            "never manual labels, engineered_for, or final outcome."
        ),
    },
    {
        "topic": "Sheet name",
        "detail": "Must be exactly: test_cases (or legacy 120_test_cases). No other sheet names.",
    },
    {
        "topic": "Strict template",
        "detail": (
            "Column names and order must match this template exactly. "
            "Custom uploads that deviate will be rejected by the agent."
        ),
    },
    {
        "topic": "persona_id",
        "detail": "Unique ID per row (e.g. F001). Required.",
    },
    {
        "topic": "simulated_user_message",
        "detail": "Opening user message before Q1. Required.",
    },
    {
        "topic": "i–viii. user input message",
        "detail": "Eight screening answers posted in order. Leave blank if persona stops early.",
    },
    {
        "topic": "i–viii. manual label",
        "detail": (
            "Gold labels per question for scoring only (eligible, ineligible, "
            "manual_review, insufficient_information or 1/0/2/3)."
        ),
    },
    {
        "topic": "ix. final eligibility outcome",
        "detail": "Gold final 4-class outcome. Required for accuracy scoring.",
    },
    {
        "topic": "engineered_for",
        "detail": "Optional metadata for analysis — never sent to the chatbot.",
    },
    {
        "topic": "API endpoints",
        "detail": (
            "OpenAI host: https://angel-flight-chatbot-app.azurewebsites.net/api/chat | "
            "Claude host: https://angel-flight-chatbot-claude.azurewebsites.net/api/chat"
        ),
    },
]

EXAMPLE_ROW: dict[str, Any] = {
    "persona_id": "F001",
    "engineered_for": "eligible",
    "simulated_user_message": "Hi, I need help getting to a medical appointment.",
    "i. user input message": "Medical appointment",
    "i. manual label": "eligible",
    "ii. user input message": "No",
    "ii. manual label": "eligible",
    "iii. user input message": "California to Arizona, about 400 miles",
    "iii. manual label": "eligible",
    "iv. user input message": "Appointment is in two weeks",
    "iv. manual label": "eligible",
    "v. user input message": "I can walk with a cane",
    "v. manual label": "eligible",
    "vi. user input message": "Stable, cleared to fly",
    "vi. manual label": "eligible",
    "vii. user input message": "Traveling alone",
    "vii. manual label": "eligible",
    "viii. user input message": "Limited income, appointment is essential",
    "viii. manual label": "eligible",
    "ix. final eligibility outcome": "eligible",
    "labeler notes": "Example row — replace with your personas.",
}


def template_columns() -> list[str]:
    cols = ["persona_id", "engineered_for", "simulated_user_message"]
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii"):
        cols.extend([f"{roman}. user input message", f"{roman}. manual label"])
    cols.extend(["ix. final eligibility outcome", "ix. manual label", "labeler notes"])
    return cols


def create_template(path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = template_columns()
    example = {c: EXAMPLE_ROW.get(c, "") for c in cols}
    cases = pd.DataFrame([example])
    readme = pd.DataFrame(README_ROWS)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        readme.to_excel(writer, sheet_name="README", index=False)
        cases.to_excel(writer, sheet_name="test_cases", index=False)
    return path


def detect_sheet(path: Path, preferred: str = "test_cases") -> str:
    xl = pd.ExcelFile(path, engine="openpyxl")
    names = [s.lower() for s in xl.sheet_names]
    for candidate in (preferred, "120_test_cases", "test_cases"):
        if candidate in names:
            return xl.sheet_names[names.index(candidate)]
    if "readme" in names and len(names) > 1:
        return xl.sheet_names[1 if names[0] == "readme" else 0]
    return xl.sheet_names[0]


def validate_workbook(path: Path, sheet: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"workbook not found: {path}")
    sheet_name = sheet or detect_sheet(path)
    df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    df.columns = df.columns.str.lower()
    issues: list[str] = []
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            issues.append(f"missing required column: {col}")
    if "persona_id" in df.columns:
        dupes = df["persona_id"].astype(str).duplicated().sum()
        if dupes:
            issues.append(f"duplicate persona_id values: {dupes}")
        if df["persona_id"].isna().any():
            issues.append("blank persona_id rows found")
    if not issues:
        missing_msgs = 0
        for col in [USER_INPUT_COLS[0]]:
            if col in df.columns and df[col].astype(str).str.strip().eq("").all():
                missing_msgs += 1
        if missing_msgs:
            issues.append("no user input messages found in column i. user input message")
    return df, issues
