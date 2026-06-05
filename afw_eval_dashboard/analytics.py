"""Derived metrics and actionable insights for the AFW eval dashboard."""
from __future__ import annotations

import pandas as pd

OUTCOME_ORDER = [
    "Eligible",
    "Ineligible",
    "Manual Review",
    "Insufficient Information",
]


def is_match(val) -> bool:
    if val is True:
        return True
    if val is False or val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    return str(val).strip().lower() in {"1", "true", "yes"}


def pct(val, digits: int = 1) -> str:
    try:
        return f"{float(val):.{digits}f}%"
    except (TypeError, ValueError):
        return "—"


def prepare_personas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "Correct Match" in out.columns:
        out["Correct Match Flag"] = out["Correct Match"].map(is_match)
    return out


def filter_runs(
    runs: pd.DataFrame,
    personas: pd.DataFrame,
    turns: pd.DataFrame,
    summary: pd.DataFrame,
    selected_runs: list[str] | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not selected_runs or runs.empty:
        return runs, personas, turns, summary
    runs_f = runs[runs["Run ID"].isin(selected_runs)]
    personas_f = personas[personas["Run ID"].isin(selected_runs)] if not personas.empty else personas
    turns_f = turns[turns["Run ID"].isin(selected_runs)] if not turns.empty else turns
    summary_f = summary[summary["Run ID"].isin(selected_runs)] if not summary.empty else summary
    return runs_f, personas_f, turns_f, summary_f


def best_run(runs: pd.DataFrame) -> pd.Series | None:
    if runs.empty or "Accuracy Pct" not in runs.columns:
        return None
    return runs.loc[runs["Accuracy Pct"].idxmax()]


def recall_matrix(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return pd.DataFrame()
    pivot = summary.pivot_table(
        index="Outcome Class",
        columns="Display Name",
        values="Recall Pct",
        aggfunc="first",
    )
    for oc in OUTCOME_ORDER:
        if oc not in pivot.index:
            pivot.loc[oc] = pd.NA
    pivot = pivot.reindex(OUTCOME_ORDER)
    return pivot


def confusion_counts(personas: pd.DataFrame) -> pd.DataFrame:
    if personas.empty or not {"Truth Label", "Predicted Label"}.issubset(personas.columns):
        return pd.DataFrame()
    return (
        personas.groupby(["Display Name", "Truth Label", "Predicted Label"], dropna=False)
        .size()
        .reset_index(name="Count")
    )


def confusion_pivot(personas: pd.DataFrame, display_name: str) -> pd.DataFrame:
    sub = personas[personas["Display Name"] == display_name] if not personas.empty else personas
    if sub.empty:
        return pd.DataFrame()
    counts = (
        sub.groupby(["Truth Label", "Predicted Label"])
        .size()
        .reset_index(name="Count")
    )
    pivot = counts.pivot(index="Truth Label", columns="Predicted Label", values="Count").fillna(0)
    for label in OUTCOME_ORDER:
        if label not in pivot.index:
            pivot.loc[label] = 0
        if label not in pivot.columns:
            pivot[label] = 0
    pivot = pivot.reindex(index=OUTCOME_ORDER, columns=OUTCOME_ORDER, fill_value=0)
    return pivot


def failures(personas: pd.DataFrame) -> pd.DataFrame:
    if personas.empty or "Correct Match Flag" not in personas.columns:
        if personas.empty or "Correct Match" not in personas.columns:
            return pd.DataFrame()
        bad = personas[~personas["Correct Match"].map(is_match)]
    else:
        bad = personas[~personas["Correct Match Flag"]]
    cols = [c for c in [
        "Display Name", "Persona ID", "Truth Label", "Predicted Label", "Error",
    ] if c in bad.columns]
    return bad[cols].sort_values(["Display Name", "Persona ID"]) if cols else bad


def top_confusion_pairs(personas: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    bad = failures(personas)
    if bad.empty:
        return pd.DataFrame()
    pairs = (
        bad.groupby(["Truth Label", "Predicted Label"])
        .size()
        .reset_index(name="Errors")
        .sort_values("Errors", ascending=False)
        .head(n)
    )
    pairs["Pattern"] = pairs["Truth Label"] + " → " + pairs["Predicted Label"]
    return pairs


def weakest_class(summary: pd.DataFrame, display_name: str) -> dict | None:
    sub = summary[summary["Display Name"] == display_name] if not summary.empty else summary
    if sub.empty or "Recall Pct" not in sub.columns:
        return None
    row = sub.loc[sub["Recall Pct"].idxmin()]
    return {
        "class": row["Outcome Class"],
        "recall": float(row["Recall Pct"]),
        "correct": int(row.get("Correct In Class", 0)),
        "total": int(row.get("Personas In Class", 0)),
    }


def executive_insights(
    runs: pd.DataFrame,
    personas: pd.DataFrame,
    summary: pd.DataFrame,
) -> list[str]:
    tips: list[str] = []
    if runs.empty:
        return ["Run the eval agent to populate benchmark data."]

    best = best_run(runs)
    if best is not None:
        tips.append(
            f"<strong>Best configuration:</strong> {best['Display Name']} "
            f"at <strong>{pct(best['Accuracy Pct'])}</strong> final-outcome accuracy "
            f"({int(best['Correct Count'])}/{int(best['Persona Count'])} personas)."
        )
        weak = weakest_class(summary, best["Display Name"])
        if weak:
            tips.append(
                f"<strong>Priority fix on best run:</strong> "
                f"{weak['class']} recall is only <strong>{pct(weak['recall'])}</strong> "
                f"({weak['correct']}/{weak['total']} correct) — focus prompt tuning here."
            )

    if not personas.empty:
        fail_n = len(failures(personas))
        total = len(personas)
        tips.append(
            f"<strong>Error volume:</strong> {fail_n:,} incorrect final outcomes "
            f"across selected runs ({pct(100 * fail_n / total if total else 0)} error rate)."
        )
        pairs = top_confusion_pairs(personas, 3)
        if not pairs.empty:
            top = pairs.iloc[0]
            tips.append(
                f"<strong>Top error pattern:</strong> Gold <em>{top['Truth Label']}</em> "
                f"misclassified as <em>{top['Predicted Label']}</em> "
                f"({int(top['Errors'])} personas)."
            )

    spread = runs["Accuracy Pct"].max() - runs["Accuracy Pct"].min() if len(runs) > 1 else 0
    if spread >= 5:
        tips.append(
            f"<strong>Model spread:</strong> {pct(spread)} gap between best and worst run — "
            "compare prompt versions before production rollout."
        )

    return tips


def mcnemar_ready(mcnemar: pd.DataFrame) -> bool:
    return (
        not mcnemar.empty
        and "Note" not in mcnemar.columns
        and "Mcnemar P Value" in mcnemar.columns
    )


def run_comparison_table(runs: pd.DataFrame) -> pd.DataFrame:
    if runs.empty:
        return runs
    cols = [
        "Display Name", "Model Display", "Prompt Label",
        "Persona Count", "Correct Count", "Accuracy Pct", "Created UTC",
    ]
    show = [c for c in cols if c in runs.columns]
    out = runs[show].sort_values("Accuracy Pct", ascending=False).copy()
    if "Accuracy Pct" in out.columns:
        best = out["Accuracy Pct"].max()
        out["Vs Best"] = out["Accuracy Pct"].apply(
            lambda v: round(float(v) - float(best), 1) if pd.notna(v) else pd.NA
        )
    return out
