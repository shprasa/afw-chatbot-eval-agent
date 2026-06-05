"""AFW Eval Agent — live dashboard (Streamlit + Plotly). Auto-updates when agent exports data."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from afw_eval_dashboard.github_loader import (
    load_tables_from_github,
    resolve_github_settings,
)

DESK = Path(__file__).resolve().parent.parent
CONFIG = DESK / "github_publish_config.txt"
DATA_CANDIDATES = [
    DESK / "workspace" / "powerbi_export",
    DESK / "AFW_Eval_Agent_Handoff" / "workspace" / "powerbi_export",
    DESK / "powerbi_export",
]


def _find_data_root() -> Path:
    for p in DATA_CANDIDATES:
        if (p / "csv" / "Evaluation_Runs.csv").is_file():
            return p
    return DATA_CANDIDATES[0]


def _has_local_export() -> bool:
    return (_find_data_root() / "csv" / "Evaluation_Runs.csv").is_file()


def _is_match(val) -> bool:
    if val is True:
        return True
    if val is False or val is None or (isinstance(val, float) and pd.isna(val)):
        return False
    return str(val).strip().lower() in {"1", "true", "yes"}


def _data_fingerprint(root: Path) -> str:
    """Change when agent writes new export files → busts cache for live updates."""
    parts: list[str] = []
    for rel in ("refresh_manifest.json", "csv/Evaluation_Runs.csv", "csv/Refresh_Log.csv"):
        p = root / rel
        if p.is_file():
            parts.append(f"{rel}:{p.stat().st_mtime_ns}:{p.stat().st_size}")
    return "|".join(parts) or "empty"


@st.cache_data(ttl=15)
def load_tables_local(data_root: str, fingerprint: str) -> dict[str, pd.DataFrame]:
    root = Path(data_root)
    csv_dir = root / "csv"

    def _read(name: str) -> pd.DataFrame:
        path = csv_dir / name
        if path.is_file():
            return pd.read_csv(path)
        return pd.DataFrame()

    tables = {
        "runs": _read("Evaluation_Runs.csv"),
        "personas": _read("Persona_Results.csv"),
        "turns": _read("Turn_Details.csv"),
        "summary": _read("Run_Summary_By_Class.csv"),
        "mcnemar": _read("McNemar_Comparisons.csv"),
        "cases": _read("User_Test_Cases.csv"),
        "refresh": _read("Refresh_Log.csv"),
    }

    manifest = root / "refresh_manifest.json"
    if manifest.is_file():
        meta = json.loads(manifest.read_text(encoding="utf-8"))
        tables["meta"] = pd.DataFrame([meta])
    return tables


@st.cache_data(ttl=15)
def load_tables_github(settings_key: str, use_config_file: bool) -> dict[str, pd.DataFrame]:
    secrets = None
    try:
        secrets = st.secrets
    except Exception:
        pass
    settings = resolve_github_settings(
        secrets=secrets,
        config_path=CONFIG if use_config_file else None,
    )
    if not settings:
        return {"runs": pd.DataFrame()}
    return load_tables_from_github(settings)


def _pct(val) -> str:
    try:
        return f"{float(val):.1f}%"
    except (TypeError, ValueError):
        return "—"


def page_executive(runs: pd.DataFrame, personas: pd.DataFrame, summary: pd.DataFrame) -> None:
    st.header("Executive Overview")

    if runs.empty:
        st.warning("No evaluation runs yet. Run the agent (menu 1) to populate data.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Evaluation Runs", len(runs))
    c2.metric("Avg Accuracy", _pct(runs["Accuracy Pct"].mean()))
    c3.metric("Best Run", runs.loc[runs["Accuracy Pct"].idxmax(), "Display Name"][:40])
    c4.metric("Persona Results", len(personas))

    left, right = st.columns([1, 1])
    with left:
        fig = px.bar(
            runs.sort_values("Accuracy Pct", ascending=True),
            x="Accuracy Pct",
            y="Display Name",
            orientation="h",
            title="Final Outcome Accuracy by Run",
            color="Model Display",
            text="Accuracy Pct",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig2 = px.scatter(
            runs,
            x="Persona Count",
            y="Accuracy Pct",
            size="Correct Count",
            color="Model Display",
            hover_name="Display Name",
            title="Accuracy vs Personas Evaluated",
        )
        fig2.update_layout(height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("All Evaluation Runs")
    show_cols = [
        "Display Name",
        "Model Display",
        "Prompt Label",
        "Persona Count",
        "Correct Count",
        "Accuracy Pct",
        "Created UTC",
    ]
    st.dataframe(runs[show_cols], use_container_width=True, hide_index=True)

    if not summary.empty:
        st.subheader("Recall by Outcome Class")
        fig3 = px.bar(
            summary,
            x="Outcome Class",
            y="Recall Pct",
            color="Display Name",
            barmode="group",
            title="Per-Class Recall Across Runs",
        )
        st.plotly_chart(fig3, use_container_width=True)


def page_personas(personas: pd.DataFrame, runs: pd.DataFrame) -> None:
    st.header("Persona Drill-Down")
    if personas.empty:
        st.info("No persona results yet.")
        return

    run_pick = st.selectbox(
        "Evaluation run",
        ["All runs"] + sorted(personas["Display Name"].dropna().unique().tolist()),
    )
    df = personas if run_pick == "All runs" else personas[personas["Display Name"] == run_pick]

    c1, c2, c3 = st.columns(3)
    correct = int(df["Correct Match"].map(_is_match).sum()) if "Correct Match" in df.columns else 0
    total = len(df)
    c1.metric("Personas", total)
    c2.metric("Correct", correct)
    c3.metric("Accuracy", _pct(100 * correct / total if total else 0))

    col_l, col_r = st.columns(2)
    with col_l:
        if "Truth Label" in df.columns:
            truth = df["Truth Label"].value_counts().reset_index()
            truth.columns = ["Outcome", "Count"]
            st.plotly_chart(
                px.pie(truth, names="Outcome", values="Count", title="Gold (Truth) Distribution"),
                use_container_width=True,
            )
    with col_r:
        if "Predicted Label" in df.columns:
            pred = df["Predicted Label"].value_counts().reset_index()
            pred.columns = ["Outcome", "Count"]
            st.plotly_chart(
                px.pie(pred, names="Outcome", values="Count", title="Predicted Distribution"),
                use_container_width=True,
            )

    if {"Truth Label", "Predicted Label"}.issubset(df.columns):
        confusion = (
            df.groupby(["Truth Label", "Predicted Label"])
            .size()
            .reset_index(name="Count")
        )
        pivot = confusion.pivot(index="Truth Label", columns="Predicted Label", values="Count").fillna(0)
        fig = px.imshow(
            pivot,
            text_auto=True,
            title="Truth vs Predicted (count)",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    persona_filter = st.multiselect(
        "Filter personas (optional)",
        sorted(df["Persona ID"].dropna().unique().tolist()),
    )
    show = df if not persona_filter else df[df["Persona ID"].isin(persona_filter)]
    cols = [c for c in [
        "Display Name",
        "Persona ID",
        "Truth Label",
        "Predicted Label",
        "Correct Match",
        "Error",
    ] if c in show.columns]
    st.dataframe(show[cols].sort_values("Persona ID"), use_container_width=True, hide_index=True)


def page_conversations(turns: pd.DataFrame, personas: pd.DataFrame) -> None:
    st.header("Conversation Transcripts")
    if turns.empty:
        st.info("No turn-level data yet.")
        return

    runs = sorted(turns["Display Name"].dropna().unique())
    run_sel = st.selectbox("Run", runs)
    sub = turns[turns["Display Name"] == run_sel]
    personas_in_run = sorted(sub["Persona ID"].dropna().unique())
    persona_sel = st.selectbox("Persona", personas_in_run)

    chat = sub[sub["Persona ID"] == persona_sel].sort_values("Turn Number")
    if chat.empty:
        st.warning("No turns for this persona.")
        return

    if not personas.empty:
        pr = personas[
            (personas["Display Name"] == run_sel) & (personas["Persona ID"] == persona_sel)
        ]
        if not pr.empty:
            row = pr.iloc[0]
            st.caption(
                f"Truth: **{row.get('Truth Label', '')}** · "
                f"Predicted: **{row.get('Predicted Label', '')}** · "
                f"Match: **{'Yes' if row.get('Correct Match') == 1 else 'No'}**"
            )

    for _, turn in chat.iterrows():
        with st.container(border=True):
            st.markdown(f"**Turn {turn.get('Turn Number', '')}** — {turn.get('Question', '')}")
            st.markdown(f"**User:** {turn.get('User Message', '')}")
            st.markdown(f"**Assistant:** {turn.get('Assistant Response', '')}")
            if pd.notna(turn.get("Checkpoint Correct")):
                ok = int(turn.get("Checkpoint Correct", 0)) == 1
                st.caption(f"Checkpoint: {'Correct' if ok else 'Incorrect'}")

    st.subheader("All turns (table)")
    show_cols = [c for c in [
        "Persona ID",
        "Turn Number",
        "Question",
        "User Message",
        "Assistant Response",
        "Checkpoint Correct",
    ] if c in chat.columns]
    st.dataframe(chat[show_cols], use_container_width=True, hide_index=True)


def page_statistics(mcnemar: pd.DataFrame) -> None:
    st.header("McNemar Comparisons")
    if mcnemar.empty or "Note" in mcnemar.columns:
        st.info(
            "No paired comparisons yet. In the eval agent, use **menu 2** "
            "to compare two runs — results will appear here automatically."
        )
        return
    st.dataframe(mcnemar, use_container_width=True, hide_index=True)


def page_test_cases(cases: pd.DataFrame) -> None:
    st.header("Gold User Test Cases")
    st.caption("Original test case columns preserved from the source Excel.")
    if cases.empty:
        st.info("No test cases loaded.")
        return

    pid = st.selectbox(
        "Persona",
        ["(show all)"] + sorted(cases["persona_id"].dropna().astype(str).unique().tolist()),
    )
    df = cases if pid == "(show all)" else cases[cases["persona_id"].astype(str) == pid]

    key_cols = [
        c
        for c in [
            "persona_id",
            "engineered_for",
            "simulated_user_message",
            "ix. final eligibility outcome",
            "ix. manual label",
            "labeler notes",
        ]
        if c in df.columns
    ]
    st.dataframe(df[key_cols] if key_cols else df, use_container_width=True, hide_index=True)

    with st.expander("All columns (full export)"):
        st.dataframe(df, use_container_width=True, hide_index=True)


def _run_script(script: Path) -> None:
    if script.is_file():
        subprocess.run([sys.executable, str(script)], cwd=str(DESK), check=False)


def _is_streamlit_cloud() -> bool:
    return Path("/mount/src").exists() or bool(os.environ.get("STREAMLIT_SHARING_MODE"))


def _is_codespace() -> bool:
    return Path("/workspaces").exists() and bool(os.environ.get("CODESPACES"))


def _team_password_ok() -> bool:
    """Optional gate via Streamlit secrets TEAM_PASSWORD (share URL + password with team)."""
    pwd = ""
    try:
        pwd = st.secrets.get("TEAM_PASSWORD", "")
    except Exception:
        pwd = os.environ.get("TEAM_PASSWORD", "")
    if not pwd:
        return True
    if st.session_state.get("team_auth"):
        return True
    st.title("AFW Eval Team Dashboard")
    st.caption("Enter the team password shared by your project lead.")
    entered = st.text_input("Password", type="password")
    if st.button("Continue", type="primary") and entered == pwd:
        st.session_state.team_auth = True
        st.rerun()
    st.stop()
    return False


def main() -> None:
    st.set_page_config(
        page_title="AFW Eval Live Dashboard",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _team_password_ok()

    st.title("Angel Flight West — Eval Dashboard")
    st.caption("UC Davis GSM MSBA · Screening chatbot evaluation · Live team view")

    st.sidebar.title("AFW Team Dashboard")
    st.sidebar.caption("UC Davis GSM MSBA · Angel Flight West Practicum")

    cloud = _is_streamlit_cloud()
    codespace = _is_codespace()
    local_ok = _has_local_export()
    secrets_obj = None
    try:
        secrets_obj = st.secrets
    except Exception:
        pass
    gh_settings = resolve_github_settings(
        secrets=secrets_obj,
        config_path=None if cloud else CONFIG,
    )

    if cloud and local_ok:
        use_github = "Local folder"
        st.sidebar.info("Streamlit Cloud — using data committed in this repo.")
    elif cloud:
        use_github = "GitHub (team live)"
        st.sidebar.info(
            f"Streamlit Cloud — live from github.com/{gh_settings['owner']}/{gh_settings['repo']}"
        )
    elif codespace and local_ok:
        use_github = "Local folder"
        st.sidebar.info("Codespace — using `workspace/powerbi_export/csv` in this repo.")
    elif gh_settings and local_ok and not cloud:
        use_github = st.sidebar.radio(
            "Data source",
            ["GitHub (team live)", "Local folder"],
            index=0,
            help="GitHub mode pulls latest CSVs from the agent repo.",
        )
    elif gh_settings:
        use_github = "GitHub (team live)"
    elif local_ok:
        use_github = "Local folder"
    else:
        use_github = st.sidebar.radio(
            "Data source",
            ["GitHub (team live)", "Local folder"],
            index=1,
            help="Set GITHUB_TOKEN env var or add workspace/powerbi_export/csv.",
        )

    live = st.sidebar.toggle("Auto-refresh (20s)", value=True)
    if live:
        st.markdown('<meta http-equiv="refresh" content="20">', unsafe_allow_html=True)

    if use_github == "GitHub (team live)":
        if not gh_settings:
            st.error(
                "GitHub not configured. Add secrets (see DEPLOY_TEAM_DASHBOARD.md) "
                "or github_publish_config.txt locally."
            )
            st.stop()
        tables = load_tables_github(
            f"{gh_settings['owner']}/{gh_settings['repo']}:{gh_settings['branch']}",
            use_config_file=not cloud,
        )
        if tables["runs"].empty:
            st.error(
                "Could not load data from GitHub. Check Streamlit secrets: "
                "`GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`."
            )
            st.stop()
        st.sidebar.success(f"Live from github.com/{gh_settings['owner']}/{gh_settings['repo']}")
    else:
        default_root = _find_data_root()
        data_root = Path(st.sidebar.text_input("Data folder", value=str(default_root)))
        if st.sidebar.button("Sync from GitHub now", use_container_width=True):
            load_tables_local.clear()
            _run_script(DESK / "sync_powerbi_from_github.py")
            st.rerun()
        if st.sidebar.button("Rebuild local export", use_container_width=True):
            load_tables_local.clear()
            _run_script(DESK / "rewrite_powerbi_exports.py")
            st.rerun()
        fp = _data_fingerprint(data_root)
        tables = load_tables_local(str(data_root), fp)
    runs = tables["runs"]
    personas = tables["personas"]
    turns = tables["turns"]
    summary = tables["summary"]
    mcnemar = tables["mcnemar"]
    cases = tables["cases"]
    refresh = tables["refresh"]

    if not refresh.empty and "Last Updated UTC" in refresh.columns:
        st.sidebar.success(f"Last export: {refresh['Last Updated UTC'].iloc[0]}")
    if "meta" in tables and not tables["meta"].empty:
        st.sidebar.metric("Runs in dataset", int(tables["meta"]["run_count"].iloc[0]))

    st.sidebar.markdown("---")
    if cloud:
        st.sidebar.markdown(
            "**Data:** github.com/shprasa/afw-chatbot-eval-agent (public)\n\n"
            "**URL:** https://afw-chatbot-eval.streamlit.app\n\n"
            "Refreshes every 20s after `python push_streamlit_dashboard.py`."
        )
    elif codespace:
        st.sidebar.markdown(
            "**Codespace:** forward port 8501 from the Ports tab to open in browser."
        )
    else:
        st.sidebar.markdown(
            "**Local URL:** http://localhost:8502\n\n"
            "**Team URL:** https://afw-chatbot-eval.streamlit.app"
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Executive Overview",
        "Persona Analysis",
        "Conversations",
        "Statistics",
        "Gold Test Cases",
    ])

    with tab1:
        page_executive(runs, personas, summary)
    with tab2:
        page_personas(personas, runs)
    with tab3:
        page_conversations(turns, personas)
    with tab4:
        page_statistics(mcnemar)
    with tab5:
        page_test_cases(cases)


if __name__ == "__main__":
    main()
