"""run the AFW chatbot over all 60 personas and score accuracy

reads the two screening workbooks, feeds each persona's 8 user-input messages
into POST /api/chat sequentially (one session per persona, reset between
personas), captures sessionData after each turn, and computes 4-class
accuracy on the final eligibility outcome plus per-question accuracy.

manual labels are never sent to the chatbot — only the user-input messages.

endpoints (per AFW docs):
  POST /api/chat            { "message": "...", "sessionId": "..." }
  POST /api/reset-session   { "sessionId": "..." }

both endpoints currently respond with regular JSON on this host even though
the API spec mentions SSE; we tolerate either by parsing the SSE "done"
event or the JSON body opportunistically.
"""
from __future__ import annotations

import json
import logging
import os
import secrets
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd

LOG = logging.getLogger("chatbot_live_eval")

DESK = Path(__file__).resolve().parent
MAIN_XLSX = DESK / "AFW User Personas Elgible - Ineligble.xlsx"
MANUAL_XLSX = DESK / "chatbot screening dataset - manual review - insufficient info.xlsx"
DATASET_120_XLSX = DESK / "AFW_120_User_Test_Cases_Composer_2.5_Batch2.xlsx"
# First-run truth encoding (1/0 checkpoints) — user-input columns are identical to MAIN_XLSX.
MAIN_TRUTH_XLSX = DESK / "AFW User Personas Elgible - Ineligble_eval_fixed.xlsx"
ARTIFACTS = Path(os.environ.get("CHATBOT_ARTIFACTS_DIR", str(DESK / "artifacts")))
REPORTS = Path(os.environ.get("CHATBOT_REPORTS_DIR", str(DESK / "reports")))

BASE_URL = os.environ.get(
    "CHATBOT_WEB_BASE_URL",
    "https://angel-flight-chatbot-app.azurewebsites.net",
).rstrip("/")
_BACKEND = os.environ.get("CHATBOT_BACKEND", "").strip().lower()
if not _BACKEND and "claude" in BASE_URL.lower():
    _BACKEND = "claude"
elif not _BACKEND:
    _BACKEND = "openai"
_OUT_SUFFIX = os.environ.get("CHATBOT_OUTPUT_SUFFIX", "").strip()
if not _OUT_SUFFIX:
    if _BACKEND == "claude":
        _OUT_SUFFIX = "_claude"
    elif os.environ.get("CHATBOT_DATASET_XLSX", "").strip() or str(
        os.environ.get("CHATBOT_USE_120_DATASET", "")
    ).lower() in ("1", "true", "yes"):
        _OUT_SUFFIX = "_120_openai"

PRED_CSV = ARTIFACTS / f"chatbot_live_predictions{_OUT_SUFFIX}.csv"
TRANSCRIPT_JSONL = ARTIFACTS / f"chatbot_live_transcripts{_OUT_SUFFIX}.jsonl"
REPORT_JSON = REPORTS / f"chatbot_live_accuracy{_OUT_SUFFIX}.json"
FAILURE_REPORT_MD = REPORTS / f"chatbot_live_failure_analysis{_OUT_SUFFIX}.md"
PROMPT_REPORT_MD = REPORTS / f"chatbot_live_prompt_improvements{_OUT_SUFFIX}.md"
CHAT_URL = f"{BASE_URL}/api/chat"
RESET_URL = f"{BASE_URL}/api/reset-session"

CANON_CLASSES: tuple[str, ...] = (
    "eligible",
    "ineligible",
    "manual_review",
    "insufficient_information",
)
DUMMY_COLS: tuple[str, ...] = (
    "is_eligible",
    "is_ineligible",
    "is_manual_review",
    "is_insufficient_information",
)
OPENING_COL = "simulated_user_message"
USER_INPUT_COLS: list[str] = [
    f"{roman}. user input message"
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")
]
# Only these columns may be POSTed to /api/chat (never labels or engineered_for).
CHAT_MESSAGE_COLS: list[str] = [OPENING_COL] + USER_INPUT_COLS
FORBIDDEN_CHAT_COLS: frozenset[str] = frozenset(
    [
        "engineered_for",
        "engineered_for_code",
        "labeler notes",
        "ix. manual label",
        "ix. final eligibility outcome",
    ]
    + [f"{r}. manual label" for r in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")]
    + [f"{r}. manual label code" for r in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")]
    + [f"{roman}. Manual Label Code" for roman in ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")]
)
MANUAL_LABEL_COLS: list[str] = [
    f"{roman}. manual label"
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")
]
QUESTION_KEYS: list[str] = [f"q{i}" for i in range(1, 9)]

REQUEST_TIMEOUT_S = float(os.environ.get("CHATBOT_TIMEOUT_S", "180"))
RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}
MAX_RETRIES = int(os.environ.get("CHATBOT_MAX_RETRIES", "5"))

RATIONALE_NOTE_FIELDS: tuple[str, ...] = (
    "outcome_notes",
    "summary_notes",
    "summary_compelling_or_financial_need_notes",
    "summary_sentiment_analysis",
    "manual_review_rationale",
)
DEFAULT_SYSTEM_PROMPT_PATH = DESK / "artifacts" / "prompt_extract_v1.txt"


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )


def canon_label(v: Any) -> str:
    """Map chatbot / text labels to four canonical classes (manual-review workbook)."""
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    raw = str(v).strip()
    if raw == "":
        return ""
    s = raw.lower().replace(".", "").replace("-", " ").replace("_", " ")
    s = " ".join(s.split())
    if "manual" in s and "review" in s:
        return "manual_review"
    if "insufficient" in s:
        return "insufficient_information"
    if ("not" in s and "eligible" in s) or s.startswith("ineligible"):
        return "ineligible"
    if s.startswith("eligible"):
        return "eligible"
    return ""


CODE_NAMES = {
    1: "eligible",
    0: "ineligible",
    2: "insufficient_information",
    3: "manual_review",
}


def text_to_code(v: Any) -> int | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)) and int(v) in CODE_NAMES:
        return int(v)
    s = str(v).strip().lower().replace(".", "").replace("-", " ")
    s = " ".join(s.split())
    if not s or s == "nan":
        return None
    if "manual" in s and "review" in s:
        return 3
    if "insufficient" in s:
        return 2
    if ("not" in s and "eligible" in s) or s.startswith("ineligible"):
        return 0
    if s.startswith("eligible"):
        return 1
    return None


def truth_final_code(row: pd.Series) -> int | None:
    if "engineered_for_code" in row.index and pd.notna(row.get("engineered_for_code")):
        return int(row["engineered_for_code"])
    return text_to_code(row.get("engineered_for"))


def truth_checkpoint_code(row: pd.Series, roman: str, fallback: int | None) -> int:
    code_col = f"{roman}. manual label code"
    if code_col in row.index and pd.notna(row.get(code_col)):
        return int(row[code_col])
    c = text_to_code(row.get(f"{roman}. manual label"))
    if c is not None:
        return c
    return fallback if fallback is not None else 2


def pred_code_from_outcome(outcome: str) -> int | None:
    return text_to_code(outcome) if outcome else None


def truth_final_binary(row: pd.Series) -> int | None:
    """Legacy binary: 1 eligible, 0 ineligible only."""
    c = truth_final_code(row)
    if c in (0, 1):
        return c
    return None


def truth_checkpoint_binary(v: Any) -> int | None:
    """Per-question manual label on eligible/ineligible sheet: 1=pass, 0=fail."""
    if pd.isna(v):
        return None
    if isinstance(v, (int, float)) and v in (0, 1):
        return int(v)
    raw = str(v).strip()
    if raw in ("1", "1.0"):
        return 1
    if raw in ("0", "0.0"):
        return 0
    return None


def pred_binary_from_outcome(outcome: str) -> int | None:
    """Chatbot eligibility_outcome -> 1 eligible, 0 ineligible, else not comparable."""
    lab = canon_label(outcome) if outcome and not str(outcome).isdigit() else ""
    if lab == "eligible" or str(outcome).strip() in ("1", "1.0"):
        return 1
    if lab == "ineligible" or str(outcome).strip() in ("0", "0.0"):
        return 0
    return None


def label_to_dummies(label: str) -> dict[str, int]:
    return {col: int(canon_label(label) == cls) for cls, col in zip(CANON_CLASSES, DUMMY_COLS)}


def ssl_context() -> ssl.SSLContext:
    """HTTPS context; certifi first, then unverified if CHATBOT_SSL_VERIFY=0."""
    if os.environ.get("CHATBOT_SSL_VERIFY", "").strip().lower() in (
        "0",
        "false",
        "no",
    ):
        return ssl._create_unverified_context()
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def load_workbook(path: Path, source_tag: str) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = df.columns.str.lower()
    df["source_workbook"] = source_tag
    return df


def _truth_columns() -> list[str]:
    cols = ["engineered_for", "engineered_for_code"]
    for roman in ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii"):
        cols.append(f"{roman}. manual label")
        cols.append(f"{roman}. manual label code")
    return cols


def merge_eligible_truth_from_backup(df: pd.DataFrame) -> pd.DataFrame:
    """Keep user-input messages from MAIN_XLSX; restore 1/0 truth from first-run backup."""
    if not MAIN_TRUTH_XLSX.is_file():
        LOG.warning(
            "truth backup missing (%s); using labels from %s",
            MAIN_TRUTH_XLSX.name,
            MAIN_XLSX.name,
        )
        return df
    truth = load_workbook(MAIN_TRUTH_XLSX, "eligible_ineligible_truth")
    keep = ["persona_id"] + [c for c in _truth_columns() if c in truth.columns]
    truth = truth[keep]
    out = df.drop(columns=[c for c in _truth_columns() if c in df.columns], errors="ignore")
    merged = out.merge(truth, on="persona_id", how="left", validate="one_to_one")
    LOG.info(
        "merged first-run truth labels from %s into %s (user inputs unchanged)",
        MAIN_TRUTH_XLSX.name,
        MAIN_XLSX.name,
    )
    return merged


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST JSON with retries; transparently parse SSE 'data: ...' streams or
    plain JSON bodies. Returns the final JSON-parsed event."""
    body = json.dumps(payload).encode("utf-8")
    last_err: BaseException | None = None
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream, application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(
                req, timeout=REQUEST_TIMEOUT_S, context=ssl_context()
            ) as resp:
                raw = resp.read().decode("utf-8", errors="replace").strip()
            if not raw:
                return {}
            if raw.startswith("data:") or "\ndata:" in raw:
                final: dict[str, Any] = {}
                for line in raw.splitlines():
                    s = line.strip()
                    if not s.startswith("data:"):
                        continue
                    chunk = s[len("data:"):].strip()
                    if not chunk:
                        continue
                    try:
                        ev = json.loads(chunk)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(ev, dict) and ev.get("type") == "done":
                        return ev
                    if isinstance(ev, dict) and ev.get("type") == "error":
                        raise RuntimeError(f"chatbot error event: {ev.get('message')}")
                    if isinstance(ev, dict):
                        final = ev
                return final
            return json.loads(raw)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in RETRYABLE_HTTP and attempt < MAX_RETRIES - 1:
                wait = min(30.0, 2.0 ** attempt)
                LOG.warning("http %s; retry in %.1fs", e.code, wait)
                time.sleep(wait)
                continue
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:400]
            except Exception:
                pass
            raise RuntimeError(f"chatbot HTTP {e.code}: {e.reason} {err_body}") from e
        except urllib.error.URLError as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                wait = min(30.0, 2.0 ** attempt)
                LOG.warning("network error %s; retry in %.1fs", e, wait)
                time.sleep(wait)
                continue
            raise RuntimeError(f"chatbot network error: {e}") from e
    raise RuntimeError(f"chatbot request exhausted retries: {last_err}")


def reset_session(session_id: str) -> None:
    try:
        post_json(RESET_URL, {"sessionId": session_id})
    except Exception as e:
        LOG.warning("reset session %s failed: %s", session_id, e)


def user_message_turns(row: pd.Series) -> list[tuple[str, str, str | None]]:
    """(column, message, question_key) — user inputs only; question_key None for opening."""
    turns: list[tuple[str, str, str | None]] = []
    opening = row.get(OPENING_COL, "")
    if not pd.isna(opening) and str(opening).strip():
        turns.append((OPENING_COL, str(opening).strip(), None))
    for q_idx, col in enumerate(USER_INPUT_COLS):
        msg = row.get(col, "")
        if pd.isna(msg) or not str(msg).strip():
            continue
        turns.append((col, str(msg).strip(), QUESTION_KEYS[q_idx]))
    for col, _, _ in turns:
        if col in FORBIDDEN_CHAT_COLS:
            raise ValueError(f"forbidden column would be sent to chatbot: {col}")
    return turns


def gather_outcome(payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Pull the canonical outcome label and the full sessionData snapshot."""
    sess = payload.get("sessionData") or {}
    if not isinstance(sess, dict):
        sess = {}
    raw = sess.get("eligibility_outcome", "")
    # the chatbot can also flip manual_review_flag or set isManualReview
    if not raw and payload.get("isManualReview"):
        raw = "manual_review"
    return canon_label(raw), sess


def run_persona(
    row: pd.Series, persona_idx: int, total: int, request_pause_s: float
) -> dict[str, Any]:
    pid = str(row["persona_id"])
    session_id = f"eval_{pid}_{secrets.token_hex(4)}"
    LOG.info("[%d/%d] persona %s session %s", persona_idx, total, pid, session_id)
    reset_session(session_id)

    per_turn: list[dict[str, Any]] = []
    final_label = ""
    final_sess: dict[str, Any] = {}
    error: str | None = None

    for col, msg, q_key in user_message_turns(row):
        turn_label = q_key or "opening"
        try:
            payload = post_json(
                CHAT_URL,
                {"message": msg, "sessionId": session_id},
            )
            pred_label, sess_snapshot = gather_outcome(payload)
            final_label = pred_label or final_label
            final_sess = sess_snapshot or final_sess
            session_rationales = extract_rationales_from_session(sess_snapshot)
            per_turn.append(
                {
                    "question": turn_label,
                    "input_col": col,
                    "user_message": msg,
                    "predicted_outcome": pred_label,
                    "isManualReview": bool(payload.get("isManualReview")),
                    "manual_review_flag": bool(sess_snapshot.get("manual_review_flag")),
                    "session_eligibility_outcome": sess_snapshot.get("eligibility_outcome"),
                    "outcome_reason_codes": sess_snapshot.get("outcome_reason_codes"),
                    "session_rationales": session_rationales,
                    "session_data": sess_snapshot,
                    "assistant_response": payload.get("response", ""),
                }
            )
        except Exception as e:
            error = f"turn {turn_label} failed: {e}"
            LOG.exception(error)
            per_turn.append(
                {
                    "question": turn_label,
                    "input_col": col,
                    "user_message": msg,
                    "error": str(e),
                }
            )
            break
        if request_pause_s > 0:
            time.sleep(request_pause_s)

    return {
        "persona_id": pid,
        "source_workbook": row.get("source_workbook", ""),
        "session_id": session_id,
        "turns": per_turn,
        "final_predicted_outcome": final_label,
        "final_session_data": final_sess,
        "error": error,
    }


def build_dataset() -> pd.DataFrame:
    dataset_path = os.environ.get("CHATBOT_DATASET_XLSX", "").strip()
    use_120 = os.environ.get("CHATBOT_USE_120_DATASET", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if dataset_path:
        path = Path(dataset_path)
    elif use_120 and DATASET_120_XLSX.is_file():
        path = DATASET_120_XLSX
    else:
        path = None
    if path is not None:
        if not path.is_file():
            raise SystemExit(f"dataset not found: {path}")
        sheet = os.environ.get("CHATBOT_DATASET_SHEET", "120_test_cases").strip()
        df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
        df.columns = df.columns.str.lower()
        df["source_workbook"] = os.environ.get(
            "CHATBOT_SOURCE_TAG", "120_test_cases_v10"
        )
        LOG.info("dataset: %d personas from %s [%s]", len(df), path.name, sheet)
        LOG.info(
            "chatbot POST columns only: %s (labels/engineered_for never sent)",
            ", ".join(CHAT_MESSAGE_COLS),
        )
        return df

    parts = []
    if MAIN_XLSX.is_file():
        # Use labels from MAIN_XLSX (1=eligible, 0=ineligible). Do not merge
        # eval_fixed backup — it mixed pass/fail with wrong q2 labels for some personas.
        parts.append(load_workbook(MAIN_XLSX, "eligible_ineligible"))
    else:
        LOG.error("missing %s", MAIN_XLSX)
    if MANUAL_XLSX.is_file():
        parts.append(load_workbook(MANUAL_XLSX, "manual_review_insufficient"))
    else:
        LOG.error("missing %s", MANUAL_XLSX)
    if not parts:
        raise SystemExit("no input workbooks found")
    df = pd.concat(parts, ignore_index=True)
    if "persona_id" not in df.columns:
        raise SystemExit("dataset missing persona_id")
    LOG.info(
        "dataset: %d personas from %s + %s",
        len(df),
        MAIN_XLSX.name,
        MANUAL_XLSX.name,
    )
    return df


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


def write_predictions_csv(rows: list[dict[str, Any]], path: Path) -> None:
    flat: list[dict[str, Any]] = []
    for r in rows:
        base = {
            "persona_id": r["persona_id"],
            "source_workbook": r["source_workbook"],
            "session_id": r["session_id"],
            "truth_label": r["truth_label"],
            "truth_binary": r.get("truth_binary", ""),
            "predicted_label": r["predicted_label"],
            "predicted_binary": r.get("predicted_binary", ""),
            "label_match": r["label_match"],
            "error": r.get("error") or "",
        }
        base.update({f"truth_{k}": v for k, v in r["truth_dummies"].items()})
        base.update({f"pred_{k}": v for k, v in r["pred_dummies"].items()})
        for qk, t in r["per_question"].items():
            base[f"truth_{qk}"] = t.get("truth_code", t["truth"])
            base[f"truth_{qk}_label"] = t.get("truth_label", "")
            base[f"pred_{qk}"] = t.get("predicted_outcome", t.get("predicted", ""))
            base[f"pred_{qk}_code"] = t.get("pred_code", "")
            base[f"match_{qk}"] = int(t["match"]) if t["match"] is not None else ""
        flat.append(base)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(flat).to_csv(path, index=False)


def compute_accuracy(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n_total = len(rows)
    n_scored = sum(1 for r in rows if r["label_match"] is not None)
    overall_correct = sum(1 for r in rows if r["label_match"] is True)
    overall_acc = (overall_correct / n_scored) if n_scored else None

    by_class: dict[str, Any] = {}
    for col in DUMMY_COLS:
        n_class = sum(1 for r in rows if r["truth_dummies"][col] == 1)
        correct = sum(
            1
            for r in rows
            if r["truth_dummies"][col] == 1 and r["label_match"] is True
        )
        by_class[col] = {
            "n_in_class": n_class,
            "correct": correct,
            "recall": (correct / n_class) if n_class else None,
        }
    by_dummy_acc: dict[str, Any] = {}
    for col in DUMMY_COLS:
        scored = [r for r in rows if r["predicted_label"]]
        if not scored:
            by_dummy_acc[col] = {"n": 0, "accuracy": None}
            continue
        agree = sum(
            1
            for r in scored
            if r["truth_dummies"][col] == r["pred_dummies"][col]
        )
        by_dummy_acc[col] = {
            "n": len(scored),
            "accuracy": agree / len(scored),
        }

    by_workbook: dict[str, Any] = {}
    for src in sorted({r["source_workbook"] for r in rows if r["source_workbook"]}):
        subset = [r for r in rows if r["source_workbook"] == src]
        n_s = sum(1 for r in subset if r["label_match"] is not None)
        c = sum(1 for r in subset if r["label_match"] is True)
        by_workbook[src] = {
            "n": len(subset),
            "n_scored": n_s,
            "correct": c,
            "accuracy": (c / n_s) if n_s else None,
        }

    by_question: dict[str, Any] = {}
    for qk in QUESTION_KEYS:
        scored = [r for r in rows if r["per_question"][qk]["match"] is not None]
        c = sum(1 for r in scored if r["per_question"][qk]["match"])
        by_question[qk] = {
            "n": len(scored),
            "correct": c,
            "accuracy": (c / len(scored)) if scored else None,
        }
    q_tot = sum(v["n"] for v in by_question.values())
    q_ok = sum(v["correct"] for v in by_question.values())

    by_wb_bin: dict[str, Any] = {}
    for src in sorted({r["source_workbook"] for r in rows}):
        sub = [r for r in rows if r["source_workbook"] == src]
        scored = [r for r in sub if r["label_match"] is not None]
        by_wb_bin[src] = {
            "n": len(sub),
            "n_scored": len(scored),
            "correct": sum(1 for r in scored if r["label_match"]),
            "accuracy": (
                sum(1 for r in scored if r["label_match"]) / len(scored)
                if scored
                else None
            ),
        }

    return {
        "encoding_note": (
            "truth/pred use 1=eligible, 0=ineligible; "
            "chatbot insufficient_information/manual_review turns are skip (not 0)"
        ),
        "by_workbook_binary": by_wb_bin,
        "n_personas": n_total,
        "n_scored": n_scored,
        "correct": overall_correct,
        "final_outcome_accuracy": overall_acc,
        "by_truth_class": by_class,
        "by_dummy_column_accuracy": by_dummy_acc,
        "by_workbook": by_workbook,
        "by_question": by_question,
        "question_level_total": q_tot,
        "question_level_correct": q_ok,
        "question_level_accuracy": (q_ok / q_tot) if q_tot else None,
    }


def fmt_pct(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{100.0 * v:.1f}%"


def extract_rationales_from_session(sess: dict[str, Any]) -> dict[str, Any]:
    """Normalize all rationale-bearing fields from sessionData."""
    if not isinstance(sess, dict):
        sess = {}
    criterion: dict[str, str] = {}
    for key, val in sess.items():
        if not isinstance(key, str) or not key.endswith("_rationale"):
            continue
        if val is None:
            continue
        text = str(val).strip()
        if text:
            criterion[key] = text
    codes_raw = sess.get("outcome_reason_codes")
    if isinstance(codes_raw, list):
        codes = [str(x).strip() for x in codes_raw if str(x).strip()]
    elif codes_raw is not None and str(codes_raw).strip():
        codes = [str(codes_raw).strip()]
    else:
        codes = []
    notes: dict[str, str] = {}
    for field in RATIONALE_NOTE_FIELDS:
        val = sess.get(field)
        if val is not None and str(val).strip():
            notes[field] = str(val).strip()
    return {
        "eligibility_outcome": str(sess.get("eligibility_outcome", "") or "").strip(),
        "outcome_reason_codes": codes,
        "criterion_rationales": criterion,
        "outcome_notes": notes.get("outcome_notes", ""),
        "summary_notes": notes.get("summary_notes", ""),
        "other_notes": {
            k: v for k, v in notes.items() if k not in ("outcome_notes", "summary_notes")
        },
    }


def load_system_prompt_text() -> str:
    path = Path(
        os.environ.get("CHATBOT_SYSTEM_PROMPT_FILE", str(DEFAULT_SYSTEM_PROMPT_PATH))
    )
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def quote_prompt_lines_containing(
    prompt: str, needles: tuple[str, ...], max_lines: int = 4
) -> list[str]:
    hits: list[str] = []
    needles_l = [n.lower() for n in needles if n]
    for raw in prompt.splitlines():
        line = raw.strip()
        if len(line) < 24:
            continue
        low = line.lower()
        if any(n in low for n in needles_l):
            hits.append(line)
            if len(hits) >= max_lines:
                break
    return hits


def _codes_from_rationales(rat: dict[str, Any]) -> list[str]:
    raw = rat.get("outcome_reason_codes", [])
    if isinstance(raw, list):
        return [str(x) for x in raw if str(x).strip()]
    if raw:
        return [str(raw)]
    return []


def _format_rationale_block(rat: dict[str, Any], max_criterion: int = 6) -> list[str]:
    lines: list[str] = []
    codes = _codes_from_rationales(rat)
    if codes:
        lines.append(f"reason_codes: {', '.join(codes)}")
    if rat.get("outcome_notes"):
        lines.append(f"outcome_notes: {rat['outcome_notes']}")
    if rat.get("summary_notes"):
        lines.append(f"summary_notes: {rat['summary_notes']}")
    crit = rat.get("criterion_rationales") or {}
    if isinstance(crit, dict):
        for k, v in list(crit.items())[:max_criterion]:
            lines.append(f"{k}: {v}")
    other = rat.get("other_notes") or {}
    if isinstance(other, dict):
        for k, v in list(other.items())[:2]:
            lines.append(f"{k}: {v}")
    return lines


def turn_rationales_for_question(row: dict[str, Any], qk: str) -> dict[str, Any]:
    for tr in row.get("turn_rationales") or []:
        if tr.get("question") == qk:
            return tr
    return {}


def first_divergence(row: dict[str, Any]) -> tuple[str, str, str]:
    for qk in QUESTION_KEYS:
        t = row.get("per_question", {}).get(qk, {})
        if t.get("match") is False:
            return qk, str(t.get("truth_label", "")), str(t.get("predicted_outcome", ""))
    return "none", "", ""


def enrich_rows_from_transcripts(
    rows: list[dict[str, Any]], path: Path
) -> list[dict[str, Any]]:
    """Backfill rationale fields for resume rows scored before rationale capture."""
    if not path.is_file():
        return rows
    full_by_pid: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            pid = str(rec.get("persona_id", "")).strip()
            if pid:
                full_by_pid[pid] = rec
    enriched: list[dict[str, Any]] = []
    for row in rows:
        out = dict(row)
        rec = full_by_pid.get(str(row.get("persona_id", "")))
        if not rec:
            enriched.append(out)
            continue
        if rec.get("final_session_data"):
            out["final_rationales"] = extract_rationales_from_session(
                rec["final_session_data"]
            )
        turns_out: list[dict[str, Any]] = []
        for t in rec.get("turns") or []:
            if t.get("session_rationales"):
                rat = t["session_rationales"]
            elif t.get("session_data"):
                rat = extract_rationales_from_session(t["session_data"])
            else:
                rat = extract_rationales_from_session(
                    {
                        "eligibility_outcome": t.get("session_eligibility_outcome"),
                        "outcome_reason_codes": t.get("outcome_reason_codes"),
                    }
                )
            turns_out.append(
                {
                    "question": t.get("question", ""),
                    "predicted_outcome": t.get("predicted_outcome", ""),
                    **rat,
                }
            )
        if turns_out:
            out["turn_rationales"] = turns_out
        enriched.append(out)
    return enriched


def build_rationale_evidence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mismatches = [r for r in rows if r.get("label_match") is False]
    confusion: Counter[tuple[str, str]] = Counter()
    reason_codes: Counter[str] = Counter()
    criterion_on_failures: Counter[str] = Counter()
    outcome_notes: Counter[str] = Counter()
    per_pair_snippets: dict[tuple[str, str], list[str]] = {}

    for r in mismatches:
        truth = str(r.get("truth_label", "") or "unknown")
        pred = str(r.get("predicted_label", "") or "unknown")
        key = (truth, pred)
        confusion[key] += 1
        final_rat = r.get("final_rationales") or {}
        for code in _codes_from_rationales(final_rat):
            reason_codes[code] += 1
        note = str(final_rat.get("outcome_notes", "") or "").strip()
        if note:
            outcome_notes[note] += 1
        crit = final_rat.get("criterion_rationales") or {}
        if isinstance(crit, dict):
            for ck, cv in crit.items():
                criterion_on_failures[f"{ck}: {cv[:120]}"] += 1
        snippet_lines = _format_rationale_block(final_rat, max_criterion=4)
        if snippet_lines:
            per_pair_snippets.setdefault(key, []).append(
                f"{r.get('persona_id')}: " + " | ".join(snippet_lines[:3])
            )
        qk, _, _ = first_divergence(r)
        if qk != "none":
            turn_rat = turn_rationales_for_question(r, qk)
            for line in _format_rationale_block(turn_rat, max_criterion=3):
                per_pair_snippets.setdefault(key, []).append(
                    f"{r.get('persona_id')} @ {qk}: {line}"
                )

    return {
        "confusion": confusion,
        "reason_codes": reason_codes,
        "criterion_on_failures": criterion_on_failures,
        "outcome_notes": outcome_notes,
        "per_pair_snippets": per_pair_snippets,
        "mismatches": mismatches,
    }


def render_failure_analysis_report(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> str:
    mismatches = [r for r in rows if r.get("label_match") is False]
    unscored = [r for r in rows if r.get("label_match") is None]
    evidence = build_rationale_evidence(rows)
    confusion = evidence["confusion"]
    by_truth: Counter[str] = Counter(str(r.get("truth_label", "") or "unknown") for r in mismatches)
    per_q_miss: Counter[str] = Counter()
    for r in mismatches:
        for qk in QUESTION_KEYS:
            t = r.get("per_question", {}).get(qk, {})
            if t.get("match") is False:
                per_q_miss[qk] += 1

    lines: list[str] = []
    lines.append("# Failure Analysis")
    lines.append("")
    lines.append("## Run Summary")
    lines.append(f"- personas: {metrics.get('n_personas', len(rows))}")
    lines.append(f"- scored final outcomes: {metrics.get('n_scored', 0)}")
    lines.append(f"- final outcome accuracy: {fmt_pct(metrics.get('final_outcome_accuracy'))}")
    lines.append(f"- incorrect matches: {len(mismatches)}")
    lines.append(f"- unscored final outcomes: {len(unscored)}")
    lines.append("")
    lines.append("## Error Concentration By Truth Class")
    if by_truth:
        for cls, n in by_truth.most_common():
            lines.append(f"- {cls}: {n} mismatches")
    else:
        lines.append("- no mismatches")
    lines.append("")
    lines.append("## Confusion Pairs")
    if confusion:
        for (truth, pred), n in confusion.most_common(10):
            lines.append(f"- truth `{truth}` predicted `{pred}`: {n}")
    else:
        lines.append("- no confusion pairs")
    lines.append("")
    lines.append("## First Divergence Checkpoint")
    if per_q_miss:
        for qk, n in per_q_miss.most_common():
            lines.append(f"- {qk}: {n} mismatches")
    else:
        lines.append("- no checkpoint divergence")
    lines.append("")
    lines.append("## Session Rationale — Outcome Reason Codes (failures only)")
    if evidence["reason_codes"]:
        for code, n in evidence["reason_codes"].most_common(12):
            lines.append(f"- `{code}`: {n}")
    else:
        lines.append("- no outcome_reason_codes on failed personas")
    lines.append("")
    lines.append("## Session Rationale — Final outcome_notes (failures only)")
    if evidence["outcome_notes"]:
        for note, n in evidence["outcome_notes"].most_common(8):
            lines.append(f"- ({n}x) {note}")
    else:
        lines.append("- no outcome_notes captured")
    lines.append("")
    lines.append("## Session Rationale — Criterion fields cited on failures")
    if evidence["criterion_on_failures"]:
        for crit, n in evidence["criterion_on_failures"].most_common(12):
            lines.append(f"- ({n}x) {crit}")
    else:
        lines.append("- no criterion *_rationale fields captured")
    lines.append("")
    lines.append("## Rationale Evidence By Confusion Pattern")
    if evidence["per_pair_snippets"]:
        for (truth, pred), _ in confusion.most_common(6):
            snippets = evidence["per_pair_snippets"].get((truth, pred), [])[:4]
            if not snippets:
                continue
            lines.append(f"### truth `{truth}` → predicted `{pred}`")
            for sn in snippets:
                lines.append(f"- {sn}")
    else:
        lines.append("- no rationale snippets tied to confusion pairs")
    lines.append("")
    lines.append("## Incorrect Personas (with session rationale)")
    if mismatches:
        for r in mismatches[:12]:
            qk, t_lbl, p_lbl = first_divergence(r)
            lines.append(
                f"### {r.get('persona_id','?')} — truth `{r.get('truth_label','')}` "
                f"vs pred `{r.get('predicted_label','')}`"
            )
            lines.append(
                f"- first divergence: {qk} (truth `{t_lbl}`, pred `{p_lbl}`)"
            )
            final_rat = r.get("final_rationales") or {}
            for line in _format_rationale_block(final_rat, max_criterion=8):
                lines.append(f"- final: {line}")
            if qk != "none":
                for line in _format_rationale_block(
                    turn_rationales_for_question(r, qk), max_criterion=5
                ):
                    lines.append(f"- at {qk}: {line}")
            lines.append("")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_prompt_improvements_report(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> str:
    by_class = metrics.get("by_truth_class", {})
    recalls = {
        "eligible": by_class.get("is_eligible", {}).get("recall"),
        "ineligible": by_class.get("is_ineligible", {}).get("recall"),
        "manual_review": by_class.get("is_manual_review", {}).get("recall"),
        "insufficient_information": by_class.get("is_insufficient_information", {}).get("recall"),
    }
    evidence = build_rationale_evidence(rows)
    confusion = evidence["confusion"]
    per_q_miss: Counter[str] = Counter()
    for r in evidence["mismatches"]:
        for qk in QUESTION_KEYS:
            if r.get("per_question", {}).get(qk, {}).get("match") is False:
                per_q_miss[qk] += 1

    prompt_text = load_system_prompt_text()
    pair_map = dict(confusion)

    def g(t: str, p: str) -> int:
        return int(pair_map.get((t, p), 0))

    lines: list[str] = []
    lines.append("# Prompt Improvement Recommendations")
    lines.append("")
    lines.append("## Data From This Run (with session rationale)")
    lines.append(f"- final outcome accuracy: {fmt_pct(metrics.get('final_outcome_accuracy'))}")
    for cls in ("insufficient_information", "manual_review", "ineligible", "eligible"):
        lines.append(f"- recall `{cls}`: {fmt_pct(recalls.get(cls))}")
    if confusion:
        (truth_top, pred_top), n_top = confusion.most_common(1)[0]
        lines.append(f"- top confusion: truth `{truth_top}` predicted `{pred_top}` ({n_top})")
    if evidence["reason_codes"]:
        top_code, top_n = evidence["reason_codes"].most_common(1)[0]
        lines.append(f"- dominant failure reason_code: `{top_code}` ({top_n} failures)")
    if per_q_miss:
        qk_top, qn = per_q_miss.most_common(1)[0]
        lines.append(f"- most frequent divergence checkpoint: {qk_top} ({qn})")
    lines.append("")
    lines.append("## REMOVE — exact clauses from the current system prompt")
    lines.append(
        "_Delete these verbatim lines/paragraphs from the prompt file "
        f"(`{os.environ.get('CHATBOT_SYSTEM_PROMPT_FILE', DEFAULT_SYSTEM_PROMPT_PATH)}`)._"
    )
    lines.append("")

    remove_blocks: list[tuple[str, list[str]]] = []
    ins_to_mr = g("insufficient_information", "manual_review")
    if ins_to_mr > 0:
        clauses = quote_prompt_lines_containing(
            prompt_text,
            ("default to Manual Review", "mixed, contradictory", "close to thresholds"),
        )
        remove_blocks.append(
            (
                f"insufficient_information → manual_review ({ins_to_mr} failures)",
                clauses
                or [
                    "If information is mixed, contradictory, or close to thresholds, default to Manual Review rather than repeated questioning."
                ],
            )
        )
    mr_to_ins = g("manual_review", "insufficient_information")
    if mr_to_ins > 0:
        clauses = quote_prompt_lines_containing(
            prompt_text,
            ("Manual Review is only allowed", "borderline", "cannot be confidently resolved"),
        )
        remove_blocks.append(
            (
                f"manual_review → insufficient_information ({mr_to_ins} failures)",
                clauses
                or [
                    "If criteria are partially met, unclear, or borderline → Manual Review",
                ],
            )
        )
    if g("ineligible", "insufficient_information") + g("ineligible", "manual_review") > 0:
        clauses = quote_prompt_lines_containing(
            prompt_text,
            ("Do not downgrade a user to Not Eligible solely because",),
        )
        remove_blocks.append(
            (
                "ineligible softened when hardship/mobility unclear",
                clauses
                or [
                    "Do not downgrade a user to Not Eligible solely because: Financial or compelling need is unclear; Mobility or medical details require confirmation; Timeline is borderline but not disqualifying",
                ],
            )
        )

    if not remove_blocks:
        lines.append("- No high-confidence removals identified from this run's error profile.")
    else:
        for title, clauses in remove_blocks:
            lines.append(f"### {title}")
            for clause in clauses:
                lines.append(f"- REMOVE: `{clause}`")
            lines.append("")

    lines.append("## ADD — exact clauses to insert into the system prompt")
    lines.append("_Paste these blocks verbatim into the prompt (Decision Rules + STEP 4 outcome section)._")
    lines.append("")

    add_blocks: list[tuple[str, list[str]]] = []

    if ins_to_mr > 0 or evidence["reason_codes"].get("DATA_INCOMPLETE", 0) >= 3:
        add_blocks.append(
            (
                "Stop escalating missing data to manual_review",
                [
                    "If any required screening field is unknown (origin, destination, travel date, mobility, medical stability, companions, financial/compelling need), set `eligibility_outcome` to `insufficient_information`, populate `outcome_reason_codes` with `DATA_INCOMPLETE`, and in `outcome_notes` list only the missing fields. Do NOT set `manual_review` until all required fields are present.",
                    "In `manual_review_rationale`, write \"N/A — insufficient_information\" when the case is missing required facts.",
                ],
            )
        )

    if mr_to_ins > 0:
        add_blocks.append(
            (
                "Borderline-but-complete cases must be manual_review",
                [
                    "When origin, destination, date, mobility, and medical stability are described but judgment is needed (seatbelt extender, mental health uncertainty, borderline notice, companion/animal constraints), set `eligibility_outcome` to `manual_review` and cite the specific criterion in `manual_review_rationale` and matching `*_rationale` fields.",
                ],
            )
        )

    if g("manual_review", "eligible") + g("manual_review", "ineligible") > 0:
        add_blocks.append(
            (
                "Safety deferral instead of hard approve/deny",
                [
                    "If operational feasibility or medical safety cannot be confirmed from the transcript, set `eligibility_outcome` to `manual_review` (not `eligible` or `ineligible`). Document the uncertainty in `manual_review_rationale` and the relevant criterion rationale field.",
                ],
            )
        )

    if g("ineligible", "insufficient_information") > 0 or g("ineligible", "manual_review") > 0:
        add_blocks.append(
            (
                "Commit to ineligible when disqualifier is confirmed",
                [
                    "When a non-negotiable disqualifier is confirmed (unsupported reason for travel, out-of-region, funeral/bereavement, distance beyond limits, confirmed financial means), set `eligibility_outcome` to `ineligible` with `REASON_FOR_TRAVEL_NOT_ELIGIBLE` or the matching code even if optional fields remain unknown.",
                ],
            )
        )

    if g("insufficient_information", "ineligible") > 0:
        add_blocks.append(
            (
                "Do not ineligible on missing facts alone",
                [
                    "Do not set `ineligible` when the only issue is missing information. Use `insufficient_information` until disqualifying facts are confirmed.",
                ],
            )
        )

    if recalls.get("eligible") is not None and recalls["eligible"] < 0.8:
        add_blocks.append(
            (
                "Eligible gate",
                [
                    "Set `eligibility_outcome` to `eligible` only when: (1) reason for travel and geography/distance pass, (2) timeline, mobility, medical stability, and financial/compelling need are satisfied, and (3) no manual-review trigger is active. Otherwise use `insufficient_information` or `manual_review`.",
                ],
            )
        )

    add_blocks.append(
        (
            "Per-turn rationale requirements (sessionData)",
            [
                "Before each `eligibility_outcome` update, refresh all `*_rationale` fields for criteria touched this turn, plus `outcome_notes` (one sentence: why this outcome now) and `summary_notes` (running screening state).",
            ],
        )
    )

    for title, clauses in add_blocks:
        lines.append(f"### {title}")
        for clause in clauses:
            lines.append(f"- ADD: `{clause}`")
        lines.append("")

    lines.append("## Rationale-driven edits tied to this run")
    if evidence["per_pair_snippets"]:
        for (truth, pred), _ in confusion.most_common(4):
            snippets = evidence["per_pair_snippets"].get((truth, pred), [])[:2]
            if not snippets:
                continue
            lines.append(f"### Pattern truth `{truth}` → `{pred}`")
            for sn in snippets:
                lines.append(f"- observed: {sn}")
    else:
        lines.append("- no per-pattern rationale snippets")
    lines.append("")
    return "\n".join(lines)


def write_iteration_reports(rows: list[dict[str, Any]], metrics: dict[str, Any]) -> tuple[Path, Path]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    failure_md = render_failure_analysis_report(rows, metrics)
    prompt_md = render_prompt_improvements_report(rows, metrics)
    FAILURE_REPORT_MD.write_text(failure_md, encoding="utf-8")
    PROMPT_REPORT_MD.write_text(prompt_md, encoding="utf-8")
    return FAILURE_REPORT_MD, PROMPT_REPORT_MD


_jsonl_lock = threading.Lock()


def append_jsonl_safe(path: Path, obj: dict[str, Any]) -> None:
    with _jsonl_lock:
        append_jsonl(path, obj)


def process_persona(
    row_s: pd.Series, i: int, iter_n: int, pause_s: float
) -> dict[str, Any]:
    try:
        result = run_persona(row_s, i, iter_n, pause_s)
    except Exception as e:
        LOG.exception("persona %s crashed", row_s.get("persona_id"))
        result = {
            "persona_id": str(row_s.get("persona_id", "")),
            "source_workbook": str(row_s.get("source_workbook", "")),
            "session_id": "",
            "turns": [],
            "final_predicted_outcome": "",
            "final_session_data": {},
            "error": str(e),
        }

    source = str(result["source_workbook"])
    pred_label = result["final_predicted_outcome"]
    pred_code = pred_code_from_outcome(pred_label)
    truth_code = truth_final_code(row_s)
    truth_bin = truth_final_binary(row_s)
    pred_bin = pred_binary_from_outcome(pred_label)
    truth_dummies = {
        col: int(canon_label(CODE_NAMES.get(truth_code, "")) == cls)
        if truth_code is not None
        else 0
        for cls, col in zip(CANON_CLASSES, DUMMY_COLS)
    }
    pred_dummies = {
        col: int(canon_label(pred_label) == cls) if pred_label else 0
        for cls, col in zip(CANON_CLASSES, DUMMY_COLS)
    }

    per_question: dict[str, dict[str, Any]] = {}
    for q_idx, qk in enumerate(QUESTION_KEYS):
        roman = ("i", "ii", "iii", "iv", "v", "vi", "vii", "viii")[q_idx]
        pred_outcome = ""
        for t in result["turns"]:
            if t.get("question") == qk:
                pred_outcome = t.get("predicted_outcome", "") or ""
                break
        t_code = truth_checkpoint_code(row_s, roman, truth_code or 2)
        p_code = pred_code_from_outcome(pred_outcome)
        match = p_code is not None and t_code == p_code
        per_question[qk] = {
            "truth": truth_bin if truth_bin is not None else t_code,
            "truth_code": t_code,
            "truth_label": CODE_NAMES.get(t_code, ""),
            "predicted": pred_bin if pred_bin is not None else p_code,
            "pred_code": p_code if p_code is not None else "",
            "predicted_outcome": pred_outcome,
            "match": match if p_code is not None else None,
        }

    match_overall = (
        truth_code == pred_code
        if truth_code is not None and pred_code is not None
        else None
    )

    reason_codes_raw = result.get("final_session_data", {}).get("outcome_reason_codes", [])
    if isinstance(reason_codes_raw, list):
        reason_codes = [str(x) for x in reason_codes_raw if str(x).strip()]
    elif reason_codes_raw is None:
        reason_codes = []
    else:
        reason_codes = [str(reason_codes_raw)]

    turn_rationales = []
    for t in result.get("turns", []):
        if t.get("session_rationales"):
            rat = t["session_rationales"]
        elif t.get("session_data"):
            rat = extract_rationales_from_session(t["session_data"])
        else:
            rat = extract_rationales_from_session(
                {
                    "eligibility_outcome": t.get("session_eligibility_outcome"),
                    "outcome_reason_codes": t.get("outcome_reason_codes"),
                }
            )
        turn_rationales.append(
            {
                "question": t.get("question", ""),
                "predicted_outcome": t.get("predicted_outcome", ""),
                **rat,
            }
        )
    final_rationales = extract_rationales_from_session(
        result.get("final_session_data") or {}
    )

    row_record = {
        "persona_id": result["persona_id"],
        "source_workbook": source,
        "session_id": result["session_id"],
        "truth_label": CODE_NAMES.get(truth_code, "") if truth_code is not None else "",
        "truth_code": truth_code,
        "truth_binary": truth_bin,
        "predicted_label": pred_label,
        "predicted_code": pred_code,
        "predicted_binary": pred_bin,
        "label_match": match_overall,
        "truth_dummies": truth_dummies,
        "pred_dummies": pred_dummies,
        "per_question": per_question,
        "final_reason_codes": reason_codes,
        "turn_rationales": turn_rationales,
        "final_rationales": final_rationales,
        "error": result.get("error"),
    }
    append_jsonl_safe(TRANSCRIPT_JSONL, {**result, "score": row_record})
    LOG.info(
        "[%d/%d] %s truth=%s pred=%s match=%s",
        i,
        iter_n,
        result["persona_id"],
        CODE_NAMES.get(truth_code, "?") if truth_code is not None else "?",
        pred_label or "?",
        match_overall if match_overall is not None else "n/a",
    )
    return row_record


def load_completed_personas(path: Path) -> set[str]:
    done: set[str] = set()
    if not path.is_file():
        return done
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("persona_id") and not rec.get("error"):
                    done.add(str(rec["persona_id"]))
            except json.JSONDecodeError:
                continue
    return done


def load_scored_rows_from_transcripts(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if rec.get("score"):
                    rows.append(rec["score"])
            except json.JSONDecodeError:
                continue
    return rows


def dedupe_scored_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep latest scored record per persona_id."""
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        pid = str(row.get("persona_id", "")).strip()
        if not pid:
            continue
        by_id[pid] = row
    return [by_id[k] for k in sorted(by_id)]


def prioritize_eval_subset(df: pd.DataFrame) -> pd.DataFrame:
    """Run harder outcome classes first when engineered_for is available."""
    if "engineered_for" not in df.columns:
        return df
    priority = {
        "insufficient_information": 0,
        "manual_review": 1,
        "ineligible": 2,
        "eligible": 3,
    }
    work = df.copy()
    work["_eval_priority"] = (
        work["engineered_for"].map(text_to_code).map(CODE_NAMES).map(priority).fillna(9)
    )
    work["_orig_order"] = range(len(work))
    work = work.sort_values(
        by=["_eval_priority", "_orig_order"],
        ascending=[True, True],
        kind="mergesort",
    ).drop(columns=["_eval_priority", "_orig_order"])
    return work


def run_eval(
    limit: int | None = None,
    pause_s: float = 0.4,
    workers: int = 1,
    resume: bool = False,
) -> dict[str, Any]:
    setup_logging()
    resume = resume or os.environ.get("CHATBOT_RESUME", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if TRANSCRIPT_JSONL.is_file() and not resume:
        TRANSCRIPT_JSONL.unlink()

    df = build_dataset()
    LOG.info(
        "backend=%s base_url=%s pred_csv=%s",
        _BACKEND or "default",
        BASE_URL,
        PRED_CSV,
    )
    LOG.info(
        "leak guard: POST uses only %s — never manual labels or engineered_for",
        ", ".join(CHAT_MESSAGE_COLS),
    )
    LOG.info(
        "loaded %d personas across %d workbooks (workers=%d)",
        len(df),
        df["source_workbook"].nunique(),
        workers,
    )

    iter_n = min(len(df), limit) if limit else len(df)
    subset = prioritize_eval_subset(df).iloc[:iter_n]
    LOG.info(
        "eval order priority: insufficient_information -> manual_review -> ineligible -> eligible"
    )
    completed = load_completed_personas(TRANSCRIPT_JSONL) if resume else set()
    if resume and completed:
        LOG.info("resume mode: skipping %d already completed personas", len(completed))
    todo: list[tuple[int, pd.Series]] = [
        (i, row_s)
        for i, (_, row_s) in enumerate(subset.iterrows(), start=1)
        if str(row_s.get("persona_id", "")) not in completed
    ]
    rows: list[dict[str, Any]] = (
        load_scored_rows_from_transcripts(TRANSCRIPT_JSONL) if resume else []
    )
    if workers <= 1:
        for i, row_s in todo:
            rows.append(process_persona(row_s, i, iter_n, pause_s))
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {
                ex.submit(process_persona, row_s, i, iter_n, pause_s): (i, row_s)
                for i, row_s in todo
            }
            for fut in as_completed(futures):
                rows.append(fut.result())
        # restore deterministic order by persona index
        order = {pid: idx for idx, (_, row_s) in enumerate(todo)
                 for pid in [str(row_s.get("persona_id", ""))]}
        rows.sort(key=lambda r: order.get(r["persona_id"], 0))

    rows = dedupe_scored_rows(rows)
    rows = enrich_rows_from_transcripts(rows, TRANSCRIPT_JSONL)
    write_predictions_csv(rows, PRED_CSV)
    metrics = compute_accuracy(rows)
    REPORTS.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(metrics, indent=2, default=str),
        encoding="utf-8",
    )
    failure_path, prompt_path = write_iteration_reports(rows, metrics)
    LOG.info("wrote %s and %s", PRED_CSV, REPORT_JSON)
    LOG.info("wrote %s and %s", failure_path, prompt_path)
    LOG.info("final accuracy: %s", metrics["final_outcome_accuracy"])
    return metrics


def regenerate_iteration_reports_only() -> dict[str, Any]:
    """Rebuild failure/prompt markdown from existing transcript + predictions."""
    setup_logging()
    rows = dedupe_scored_rows(load_scored_rows_from_transcripts(TRANSCRIPT_JSONL))
    rows = enrich_rows_from_transcripts(rows, TRANSCRIPT_JSONL)
    if not rows and PRED_CSV.is_file():
        import pandas as pd

        df = pd.read_csv(PRED_CSV)
        rows = df.to_dict(orient="records")
        rows = enrich_rows_from_transcripts(rows, TRANSCRIPT_JSONL)
    metrics = compute_accuracy(rows)
    failure_path, prompt_path = write_iteration_reports(rows, metrics)
    LOG.info("regenerated %s and %s", failure_path, prompt_path)
    return metrics


if __name__ == "__main__":
    if os.environ.get("CHATBOT_REGEN_REPORTS_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        out = regenerate_iteration_reports_only()
        print(json.dumps(out, indent=2, default=str))
    else:
        raw_limit = os.environ.get("CHATBOT_EVAL_LIMIT", "").strip()
        lim = int(raw_limit) if raw_limit.isdigit() else None
        pause = float(os.environ.get("CHATBOT_TURN_PAUSE_S", "0.4"))
        workers = int(os.environ.get("CHATBOT_PARALLEL_WORKERS", "6"))
        resume = os.environ.get("CHATBOT_RESUME", "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        out = run_eval(limit=lim, pause_s=pause, workers=workers, resume=resume)
        print(json.dumps(out, indent=2, default=str))
