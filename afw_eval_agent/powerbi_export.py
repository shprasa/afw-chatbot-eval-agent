"""Dashboard CSV export from workspace runs — auto-refreshes after each eval."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import AGENT_ROOT, Workspace
from .template import detect_sheet

OUTCOME_LABELS = {
    "eligible": "Eligible",
    "ineligible": "Ineligible",
    "insufficient_information": "Insufficient Information",
    "manual_review": "Manual Review",
    "insufficient information": "Insufficient Information",
    "manual review": "Manual Review",
}

QUESTION_ORDER = ["Opening"] + [f"Question {i}" for i in range(1, 9)]
QUESTION_KEYS = ["opening"] + [f"q{i}" for i in range(1, 9)]


def _title_case_column(col: str) -> str:
    """Convert snake_case / raw names to readable Power BI column titles."""
    known = {
        "persona_id": "Persona ID",
        "run_id": "Run ID",
        "run_label": "Run Label",
        "display_name": "Display Name",
        "model_key": "Model Key",
        "model_display": "Model Display",
        "api_base_url": "API Base URL",
        "prompt_key": "Prompt Key",
        "prompt_label": "Prompt Label",
        "dataset_xlsx": "Dataset File",
        "dataset_sheet": "Dataset Sheet",
        "created_utc": "Created UTC",
        "output_suffix": "Output Suffix",
        "source_workbook": "Source Workbook",
        "session_id": "Session ID",
        "truth_label": "Truth Label",
        "predicted_label": "Predicted Label",
        "label_match": "Correct Match",
        "truth_binary": "Truth Binary",
        "predicted_binary": "Predicted Binary",
        "truth_is_eligible": "Truth Is Eligible",
        "truth_is_ineligible": "Truth Is Ineligible",
        "truth_is_manual_review": "Truth Is Manual Review",
        "truth_is_insufficient_information": "Truth Is Insufficient Information",
        "pred_is_eligible": "Predicted Is Eligible",
        "pred_is_ineligible": "Predicted Is Ineligible",
        "pred_is_manual_review": "Predicted Is Manual Review",
        "pred_is_insufficient_information": "Predicted Is Insufficient Information",
        "engineered_for": "Engineered For",
        "simulated_user_message": "Simulated User Message",
        "ix. final eligibility outcome": "Final Eligibility Outcome",
        "ix. manual label": "Final Manual Label",
        "labeler notes": "Labeler Notes",
    }
    low = col.strip().lower()
    if low in known:
        return known[low]
    if low in OUTCOME_LABELS:
        return OUTCOME_LABELS[low]
    if re.match(r"^[ivx]+\. ", low):
        parts = col.split(".", 1)
        roman = parts[0].strip().upper()
        rest = parts[1].strip() if len(parts) > 1 else ""
        return f"{roman}. {rest.title()}"
    text = col.replace("_", " ").strip()
    return text.title() if text else col


def _rename_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [_title_case_column(str(c)) for c in out.columns]
    return out


def _pretty_outcome(val: Any) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip()
    return OUTCOME_LABELS.get(s.lower().replace(" ", "_"), s.replace("_", " ").title())


def _repo_roots(ws: Workspace) -> list[Path]:
    roots = [AGENT_ROOT, ws.root.parent, AGENT_ROOT / "AFW_Eval_Agent_Handoff"]
    out: list[Path] = []
    seen: set[str] = set()
    for r in roots:
        key = str(r.resolve()) if r.exists() else str(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def _resolve_path(rel_or_abs: str, ws: Workspace) -> Path:
    p = Path(rel_or_abs)
    if p.is_file():
        return p
    if not rel_or_abs:
        return p
    rel = rel_or_abs.replace("\\", "/")
    candidates = [p]
    if not p.is_absolute():
        for root in _repo_roots(ws):
            candidates.append(root / rel)
        if rel.startswith("workspace/"):
            candidates.append(ws.root.parent / rel)
            candidates.append(ws.root / rel.replace("workspace/", "", 1))
    for cand in candidates:
        if cand.is_file():
            return cand
    return candidates[-1] if candidates else p


def _load_transcripts(path: Path) -> dict[str, dict]:
    by_pid: dict[str, dict] = {}
    if not path.is_file():
        return by_pid
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        pid = str(rec.get("persona_id", "")).strip()
        if pid:
            by_pid[pid] = rec
    return by_pid


def _load_user_test_cases(runs: list[dict], ws: Workspace) -> pd.DataFrame:
    """Preserve original Excel columns exactly (no lowercasing)."""
    frames: list[pd.DataFrame] = []
    seen: set[str] = set()
    for run in runs:
        candidates: list[Path] = []
        dataset_rel = run.get("dataset_xlsx", "")
        if dataset_rel:
            p = _resolve_path(dataset_rel, ws)
            if p.is_file() and p.suffix.lower() == ".xlsx":
                candidates.append(p)
        pred_art = run.get("artifacts", {}).get("predictions", "")
        if pred_art:
            run_dir = _resolve_path(pred_art, ws).parent
            if run_dir.is_dir():
                for f in run_dir.glob("*.xlsx"):
                    if f.is_file():
                        candidates.append(f)
        for xlsx in candidates:
            if not xlsx.is_file():
                continue
            key = str(xlsx.resolve())
            if key in seen:
                continue
            seen.add(key)
            sheet = detect_sheet(xlsx)
            df = pd.read_excel(xlsx, sheet_name=sheet, engine="openpyxl")
            df.insert(0, "Source Dataset File", xlsx.name)
            df.insert(1, "Source Sheet Name", sheet)
            frames.append(df)
    if not frames:
        for root in _repo_roots(ws):
            fallback = root / "data" / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
            if fallback.is_file():
                sheet = detect_sheet(fallback)
                df = pd.read_excel(fallback, sheet_name=sheet, engine="openpyxl")
                df.insert(0, "Source Dataset File", fallback.name)
                df.insert(1, "Source Sheet Name", sheet)
                frames.append(df)
                break
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _load_run_predictions(run: dict, ws: Workspace) -> pd.DataFrame:
    pred_path = _resolve_path(run.get("predictions_csv", ""), ws)
    if not pred_path.is_file():
        return pd.DataFrame()
    return pd.read_csv(pred_path).drop_duplicates("persona_id", keep="last")


def _scores_from_predictions(pred: pd.DataFrame) -> tuple[int | None, int | None, float | None]:
    if pred.empty or "label_match" not in pred.columns:
        return None, None, None
    n = len(pred)
    correct = int(pred["label_match"].astype(bool).sum())
    accuracy = round(100.0 * correct / n, 1) if n else None
    return n, correct, accuracy


def _build_evaluation_runs(runs: list[dict], ws: Workspace) -> pd.DataFrame:
    rows: list[dict] = []
    for run in runs:
        pred = _load_run_predictions(run, ws)
        n_personas, correct, accuracy_pct = _scores_from_predictions(pred)

        arts = run.get("artifacts", {}) or {}
        acc_rel = arts.get("accuracy") or arts.get("chatbot_live_accuracy", "")
        acc_path = _resolve_path(acc_rel, ws)
        if n_personas is None and acc_path.is_file():
            acc = json.loads(acc_path.read_text(encoding="utf-8"))
            n_personas = acc.get("n_personas")
            correct = acc.get("correct")
            acc_val = acc.get("final_outcome_accuracy")
            accuracy_pct = round(float(acc_val) * 100, 1) if acc_val is not None else None

        rows.append(
            {
                "run_id": run.get("run_id", ""),
                "run_label": run.get("run_label", ""),
                "display_name": run.get("display_name", ""),
                "model_display": run.get("model_display", ""),
                "prompt_label": run.get("prompt_label", ""),
                "api_base_url": run.get("api_base_url", ""),
                "dataset_file": Path(str(run.get("dataset_xlsx", ""))).name,
                "dataset_sheet": run.get("dataset_sheet", ""),
                "created_utc": run.get("created_utc", ""),
                "persona_count": n_personas,
                "correct_count": correct,
                "accuracy_pct": accuracy_pct,
            }
        )
    return _rename_df(pd.DataFrame(rows))


def _build_persona_results(runs: list[dict], ws: Workspace) -> pd.DataFrame:
    rows: list[dict] = []
    for run in runs:
        pred_path = _resolve_path(run.get("predictions_csv", ""), ws)
        if not pred_path.is_file():
            continue
        pred = _load_run_predictions(run, ws)
        if pred.empty:
            continue
        for _, r in pred.iterrows():
            rows.append(
                {
                    "run_id": run.get("run_id", ""),
                    "run_label": run.get("run_label", ""),
                    "display_name": run.get("display_name", ""),
                    "model_display": run.get("model_display", ""),
                    "prompt_label": run.get("prompt_label", ""),
                    "persona_id": r.get("persona_id", ""),
                    "session_id": r.get("session_id", ""),
                    "truth_label": _pretty_outcome(r.get("truth_label")),
                    "predicted_label": _pretty_outcome(r.get("predicted_label")),
                    "correct_match": bool(r.get("label_match")),
                    "truth_is_eligible": r.get("truth_is_eligible"),
                    "truth_is_ineligible": r.get("truth_is_ineligible"),
                    "truth_is_manual_review": r.get("truth_is_manual_review"),
                    "truth_is_insufficient_information": r.get("truth_is_insufficient_information"),
                    "predicted_is_eligible": r.get("pred_is_eligible"),
                    "predicted_is_ineligible": r.get("pred_is_ineligible"),
                    "predicted_is_manual_review": r.get("pred_is_manual_review"),
                    "predicted_is_insufficient_information": r.get("pred_is_insufficient_information"),
                    "error": r.get("error", ""),
                }
            )
    return _rename_df(pd.DataFrame(rows))


def _build_turn_details(runs: list[dict], ws: Workspace) -> pd.DataFrame:
    rows: list[dict] = []
    q_display = {"opening": "Opening"}
    for i in range(1, 9):
        q_display[f"q{i}"] = f"Question {i}"

    for run in runs:
        arts = run.get("artifacts", {}) or {}
        t_rel = arts.get("transcripts") or arts.get("chatbot_live_transcripts", "")
        t_path = _resolve_path(t_rel, ws)
        transcripts = _load_transcripts(t_path)
        for pid, rec in transcripts.items():
            for idx, turn in enumerate(rec.get("turns") or []):
                q = str(turn.get("question", "") or "")
                rows.append(
                    {
                        "run_id": run.get("run_id", ""),
                        "display_name": run.get("display_name", ""),
                        "persona_id": pid,
                        "turn_number": idx + 1,
                        "question": q_display.get(q, q.replace("_", " ").title()),
                        "user_message": turn.get("user_message", ""),
                        "assistant_response": turn.get("assistant_response", ""),
                        "predicted_outcome": _pretty_outcome(turn.get("predicted_outcome")),
                        "session_eligibility_outcome": _pretty_outcome(
                            turn.get("session_eligibility_outcome")
                        ),
                        "checkpoint_correct": turn.get("checkpoint_correct"),
                    }
                )
    return _rename_df(pd.DataFrame(rows))


def _build_run_summary(runs: list[dict], ws: Workspace) -> pd.DataFrame:
    rows: list[dict] = []
    for run in runs:
        pred = _load_run_predictions(run, ws)
        if not pred.empty and "truth_label" in pred.columns:
            pred = pred.copy()
            pred["gold_truth"] = pred["truth_label"].map(_pretty_outcome)
            for label, grp in pred.groupby("gold_truth"):
                if not label:
                    continue
                scored = grp.dropna(subset=["label_match"])
                n_in = len(grp)
                n_correct = int(scored["label_match"].astype(bool).sum()) if not scored.empty else 0
                recall = round(100.0 * n_correct / n_in, 1) if n_in else None
                rows.append(
                    {
                        "run_id": run.get("run_id", ""),
                        "display_name": run.get("display_name", ""),
                        "outcome_class": label,
                        "personas_in_class": n_in,
                        "correct_in_class": n_correct,
                        "recall_pct": recall,
                    }
                )
            continue

        arts = run.get("artifacts", {}) or {}
        acc_rel = arts.get("accuracy") or arts.get("chatbot_live_accuracy", "")
        acc_path = _resolve_path(acc_rel, ws)
        if not acc_path.is_file():
            continue
        acc = json.loads(acc_path.read_text(encoding="utf-8"))
        for class_key, stats in (acc.get("by_truth_class") or {}).items():
            label = class_key.replace("is_", "").replace("_", " ").title()
            rows.append(
                {
                    "run_id": run.get("run_id", ""),
                    "display_name": run.get("display_name", ""),
                    "outcome_class": label,
                    "personas_in_class": stats.get("n_in_class"),
                    "correct_in_class": stats.get("correct"),
                    "recall_pct": round(float(stats.get("recall", 0)) * 100, 1)
                    if stats.get("recall") is not None
                    else None,
                }
            )
    return _rename_df(pd.DataFrame(rows))


def _build_mcnemar(workspace: Workspace) -> pd.DataFrame:
    rows: list[dict] = []
    for p in sorted(workspace.comparisons.glob("mcnemar_*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        rows.append(
            {
                "comparison_file": p.name,
                "group_a": d.get("name_a", ""),
                "group_b": d.get("name_b", ""),
                "paired_personas": d.get("n_paired"),
                "accuracy_a_pct": round(float(d.get("accuracy_a", 0)) * 100, 1),
                "accuracy_b_pct": round(float(d.get("accuracy_b", 0)) * 100, 1),
                "ate_percentage_points": round(float(d.get("ate_b_minus_a_pp", 0)), 1),
                "a_only_correct": d.get("a_only_correct"),
                "b_only_correct": d.get("b_only_correct"),
                "mcnemar_p_value": d.get("mcnemar_p_value"),
                "significant_at_0_05": d.get("significant_at_0_05"),
            }
        )
    return _rename_df(pd.DataFrame(rows))


def _data_dictionary() -> pd.DataFrame:
    rows = [
        ("User Test Cases", "Original persona workbook — columns preserved exactly from source Excel."),
        ("Evaluation Runs", "One row per agent evaluation run."),
        ("Persona Results", "One row per persona per run with truth vs predicted labels."),
        ("Turn Details", "One row per chatbot conversation turn."),
        ("Run Summary By Class", "Recall by gold outcome class for each run."),
        ("McNemar Comparisons", "Paired statistical comparisons between two runs."),
        ("Refresh Log", "Timestamp of last export — use for Power BI refresh tracking."),
    ]
    return pd.DataFrame(rows, columns=["Table Name", "Description"])


def export_powerbi_data(workspace: Workspace | None = None) -> Path:
    """Write clean Excel + CSV folder to workspace/powerbi_export/."""
    ws = workspace or Workspace()
    ws.ensure_dirs()
    out_dir = ws.powerbi_export
    csv_dir = out_dir / "csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    runs = ws.load_manifest()
    user_cases = _load_user_test_cases(runs, ws)
    eval_runs = _build_evaluation_runs(runs, ws)
    persona_results = _build_persona_results(runs, ws)
    turn_details = _build_turn_details(runs, ws)
    run_summary = _build_run_summary(runs, ws)
    mcnemar = _build_mcnemar(ws)
    dictionary = _data_dictionary()
    refresh = pd.DataFrame(
        [{"Last Updated UTC": datetime.now(timezone.utc).isoformat(), "Run Count": len(runs)}]
    )

    xlsx_path = out_dir / "AFW_PowerBI_Data.xlsx"
    sheets: list[tuple[str, pd.DataFrame]] = [
        ("User Test Cases", user_cases),
        ("Evaluation Runs", eval_runs),
        ("Persona Results", persona_results),
        ("Turn Details", turn_details),
        ("Run Summary By Class", run_summary),
        ("McNemar Comparisons", mcnemar),
        ("Data Dictionary", dictionary),
        ("Refresh Log", refresh),
    ]

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, df in sheets:
            if df is None or df.empty:
                pd.DataFrame({"Note": [f"No data yet for {name}"]}).to_excel(
                    writer, sheet_name=name[:31], index=False
                )
            else:
                df.to_excel(writer, sheet_name=name[:31], index=False)

    for name, df in sheets:
        safe = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
        if df is None:
            continue
        if df.empty and name != "McNemar Comparisons":
            continue
        if df.empty and name == "McNemar Comparisons":
            df = pd.DataFrame(
                columns=[
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
            )
        df.to_csv(csv_dir / f"{safe}.csv", index=False, encoding="utf-8-sig")

    try:
        xlsx_rel = str(xlsx_path.resolve().relative_to(AGENT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        xlsx_rel = str(xlsx_path)
    meta = {
        "last_updated_utc": datetime.now(timezone.utc).isoformat(),
        "run_count": len(runs),
        "xlsx": xlsx_rel,
        "csv_folder": "workspace/powerbi_export/csv",
    }
    (out_dir / "refresh_manifest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return xlsx_path
