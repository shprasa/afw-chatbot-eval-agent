"""AFW Screening Chatbot Evaluation Dashboard — Streamlit + Plotly."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from afw_eval_dashboard.analytics import (
    OUTCOME_ORDER,
    confusion_pivot,
    failures,
    filter_runs,
    pct,
    prepare_personas,
    recall_matrix,
    run_comparison_table,
    top_confusion_pairs,
)
from afw_eval_dashboard.mcnemar_loader import (
    comparison_summary_df,
    list_comparisons_github,
    list_comparisons_local,
    load_comparison_json,
)
from afw_eval_dashboard.github_loader import (
    load_tables_from_github,
    resolve_github_settings,
)
from afw_eval_dashboard.theme import (
    BRAND,
    CHART_HEIGHT,
    CHART_HEIGHT_TALL,
    OUTCOME_COLORS,
    brand_header,
    chart_layout,
    hero,
    inject_css,
    insight,
)

DESK = Path(__file__).resolve().parent.parent
CONFIG = DESK / "github_publish_config.txt"
DATA_CANDIDATES = [
    DESK / "workspace" / "powerbi_export",
    DESK / "AFW_Eval_Agent_Handoff" / "workspace" / "powerbi_export",
    DESK / "powerbi_export",
]


# ── Data loading ─────────────────────────────────────────────────────────────

def _find_data_root() -> Path:
    for p in DATA_CANDIDATES:
        if (p / "csv" / "Evaluation_Runs.csv").is_file():
            return p
    return DATA_CANDIDATES[0]


def _has_local_export() -> bool:
    return (_find_data_root() / "csv" / "Evaluation_Runs.csv").is_file()


def _data_fingerprint(root: Path) -> str:
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
        return pd.read_csv(path) if path.is_file() else pd.DataFrame()

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
        tables["meta"] = pd.DataFrame([json.loads(manifest.read_text(encoding="utf-8"))])
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


# ── Pages (Power BI guide alignment) ─────────────────────────────────────────

def page_run_overview(runs: pd.DataFrame, personas: pd.DataFrame) -> None:
    hero("Run Overview", "Live metrics — updates when new evals are saved to the repo")

    if runs.empty:
        st.warning("No evaluation runs yet. Use the **Eval Agent** tab to run an evaluation.")
        return

    best = runs.loc[runs["Accuracy Pct"].idxmax()]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Evaluation Arms", len(runs))
    c2.metric("Mean Accuracy", pct(runs["Accuracy Pct"].mean()))
    c3.metric("Best Accuracy", pct(best["Accuracy Pct"]))
    c4.metric("Personas Scored", f"{int(personas['Persona ID'].nunique()) if not personas.empty else 0:,}")
    c5.metric("Total Errors", f"{len(failures(personas)):,}")

    left, right = st.columns([3, 2])
    with left:
        ordered = runs.sort_values("Accuracy Pct", ascending=True)
        fig = px.bar(
            ordered,
            x="Accuracy Pct",
            y="Display Name",
            orientation="h",
            color="Model Display",
            text="Accuracy Pct",
            labels={"Accuracy Pct": "Accuracy %", "Display Name": ""},
            title="Final Outcome Accuracy by Arm",
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        chart_layout(fig, height=CHART_HEIGHT_TALL, extra_bottom=40)
        fig.update_layout(yaxis=dict(automargin=True))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig2 = go.Figure(go.Scatter(
            x=runs["Persona Count"],
            y=runs["Accuracy Pct"],
            mode="markers+text",
            text=runs["Prompt Label"],
            textposition="top center",
            marker=dict(
                size=runs["Correct Count"] / 3 + 10,
                color=runs["Accuracy Pct"],
                colorscale=[[0, BRAND["bright_red"]], [0.5, BRAND["orange"]], [1, BRAND["ocean"]]],
                showscale=True,
                colorbar=dict(title="Acc %"),
            ),
            hovertext=runs["Display Name"],
            hoverinfo="text+x+y",
        ))
        fig2.update_layout(
            title="Accuracy vs Coverage",
            xaxis_title="Personas",
            yaxis_title="Accuracy %",
        )
        chart_layout(fig2, height=CHART_HEIGHT)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Arm Comparison Table")
    styled = run_comparison_table(runs)
    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Accuracy Pct": st.column_config.NumberColumn(format="%.1f%%"),
            "Vs Best": st.column_config.NumberColumn("Δ vs Best (pp)", format="%.1f"),
        },
    )


def page_accuracy_by_class(summary: pd.DataFrame, runs: pd.DataFrame) -> None:
    hero("Accuracy by Class", "Per-class recall matrix — Power BI guide § Accuracy by class")

    if summary.empty:
        st.info("No per-class summary available.")
        return

    mat = recall_matrix(summary)
    if mat.empty:
        st.info("No recall data.")
        return

    fig = px.imshow(
        mat,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale=[[0, "#FEE2E2"], [0.5, "#FEF3C7"], [1, "#DCFCE7"]],
        labels=dict(color="Recall %"),
        title="Recall by Truth Outcome Class (rows) × Evaluation Arm (columns)",
    )
    chart_layout(fig, height=CHART_HEIGHT_TALL, extra_bottom=20)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Class Detail")
    run_pick = st.selectbox(
        "Focus arm",
        sorted(summary["Display Name"].dropna().unique()),
        key="class_run",
    )
    sub = summary[summary["Display Name"] == run_pick].copy()
    sub = sub.set_index("Outcome Class").reindex(OUTCOME_ORDER).reset_index()
    sub = sub.dropna(subset=["Recall Pct"])

    col1, col2 = st.columns([2, 1])
    with col1:
        fig2 = px.bar(
            sub,
            x="Outcome Class",
            y="Recall Pct",
            color="Outcome Class",
            color_discrete_map=OUTCOME_COLORS,
            text="Recall Pct",
            title=f"Recall by Class — {run_pick}",
        )
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(showlegend=False, height=360)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        if not sub.empty:
            worst = sub.loc[sub["Recall Pct"].idxmin()]
            insight(
                f"<strong>Action:</strong> Improve <em>{worst['Outcome Class']}</em> handling — "
                f"only <strong>{pct(worst['Recall Pct'])}</strong> recall "
                f"({int(worst['Correct In Class'])}/{int(worst['Personas In Class'])})."
            )
        st.dataframe(
            sub[["Outcome Class", "Personas In Class", "Correct In Class", "Recall Pct"]],
            hide_index=True,
            use_container_width=True,
        )


def page_confusion(personas: pd.DataFrame) -> None:
    hero("Confusion Analysis", "Truth × predicted outcome — Power BI guide § Confusion")

    if personas.empty:
        st.info("No persona results.")
        return

    runs = sorted(personas["Display Name"].dropna().unique())
    run_sel = st.selectbox("Evaluation arm", runs, key="conf_run")

    pivot = confusion_pivot(personas, run_sel)
    if pivot.empty:
        st.warning("No confusion data for this arm.")
        return

    fig = px.imshow(
        pivot,
        text_auto=True,
        color_continuous_scale="Blues",
        labels=dict(x="Predicted", y="Truth", color="Count"),
        title=f"Confusion Matrix — {run_sel}",
    )
    chart_layout(fig, height=CHART_HEIGHT_TALL)
    st.plotly_chart(fig, use_container_width=True)

    pairs = top_confusion_pairs(
        personas[personas["Display Name"] == run_sel], n=8
    )
    if not pairs.empty:
        st.subheader("Top Misclassification Patterns")
        fig2 = px.bar(
            pairs,
            x="Errors",
            y="Pattern",
            orientation="h",
            title="Most frequent truth → predicted errors",
            color="Errors",
            color_continuous_scale=[[0, BRAND["light_blue"]], [1, BRAND["bright_red"]]],
        )
        fig2.update_layout(showlegend=False)
        chart_layout(fig2, height=CHART_HEIGHT, extra_bottom=30)
        st.plotly_chart(fig2, use_container_width=True)
        insight(
            "<strong>Prompt tuning:</strong> Review transcripts for the top patterns above "
            "in the Failure Review tab — these drive the largest accuracy gains."
        )


def page_failure_review(personas: pd.DataFrame, turns: pd.DataFrame) -> None:
    hero("Failure Review", "Actionable error queue for prompt and policy improvements")

    bad = failures(personas)
    if bad.empty:
        st.success("No failures in the selected runs.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Failed Personas", len(bad))
    patterns = top_confusion_pairs(personas, 1)
    if not patterns.empty:
        c2.metric("Top Error Pattern", patterns.iloc[0]["Pattern"][:28])
        c3.metric("Count", int(patterns.iloc[0]["Errors"]))

    pattern_filter = st.multiselect(
        "Filter by truth outcome",
        sorted(bad["Truth Label"].dropna().unique()),
    )
    show = bad if not pattern_filter else bad[bad["Truth Label"].isin(pattern_filter)]

    st.dataframe(
        show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Truth Label": st.column_config.TextColumn("Truth"),
            "Predicted Label": st.column_config.TextColumn("Predicted"),
        },
    )

    if not turns.empty and "Display Name" in show.columns:
        st.subheader("Inspect Conversation")
        row_idx = st.selectbox(
            "Select failure",
            range(len(show)),
            format_func=lambda i: (
                f"{show.iloc[i]['Persona ID']} — "
                f"{show.iloc[i]['Truth Label']} → {show.iloc[i]['Predicted Label']}"
            ),
        )
        row = show.iloc[row_idx]
        chat = turns[
            (turns["Display Name"] == row["Display Name"])
            & (turns["Persona ID"] == row["Persona ID"])
        ].sort_values("Turn Number")
        for _, turn in chat.iterrows():
            with st.container(border=True):
                st.markdown(f"**Turn {turn.get('Turn Number', '')}** · {turn.get('Question', '')}")
                st.markdown(f"**User:** {turn.get('User Message', '')}")
                st.markdown(f"**Assistant:** {turn.get('Assistant Response', '')}")


def page_conversations(turns: pd.DataFrame, personas: pd.DataFrame) -> None:
    hero("Conversations", "Full transcript drill-down by arm and persona")

    if turns.empty:
        st.info("No turn-level data.")
        return

    runs = sorted(turns["Display Name"].dropna().unique())
    run_sel = st.selectbox("Run", runs, key="conv_run")
    sub = turns[turns["Display Name"] == run_sel]
    persona_sel = st.selectbox(
        "Persona",
        sorted(sub["Persona ID"].dropna().unique()),
        key="conv_persona",
    )
    chat = sub[sub["Persona ID"] == persona_sel].sort_values("Turn Number")

    if not personas.empty:
        pr = personas[
            (personas["Display Name"] == run_sel) & (personas["Persona ID"] == persona_sel)
        ]
        if not pr.empty:
            r = pr.iloc[0]
            match = r.get("Correct Match Flag", r.get("Correct Match"))
            from afw_eval_dashboard.analytics import is_match
            ok = is_match(match)
            st.markdown(
                f"**Truth:** `{r.get('Truth Label', '')}` · "
                f"**Predicted:** `{r.get('Predicted Label', '')}` · "
                f"**Match:** {'✅' if ok else '❌'}"
            )

    for _, turn in chat.iterrows():
        with st.container(border=True):
            st.markdown(f"**Turn {turn.get('Turn Number', '')}** — {turn.get('Question', '')}")
            st.markdown(f"**User:** {turn.get('User Message', '')}")
            st.markdown(f"**Assistant:** {turn.get('Assistant Response', '')}")


def page_mcnemar_test(
    mcnemar: pd.DataFrame,
    gh_settings: dict[str, str] | None,
    workspace_root: Path,
) -> None:
    hero("McNemar's Test", "Paired comparison from Eval Agent → McNemar comparison")

    comparisons = list_comparisons_local(workspace_root)
    if not comparisons and gh_settings:
        comparisons = list_comparisons_github(gh_settings)

    if not comparisons:
        st.info(
            "No McNemar comparisons yet. In the **Eval Agent** tab, open **McNemar comparison**, "
            "pick Group A and Group B, then save results to the GitHub repo."
        )
        return

    pick = st.selectbox(
        "Comparison (from agent menu 2)",
        comparisons,
        format_func=lambda x: x["label"],
    )

    local_path = Path(pick["path"]) if pick.get("source") == "local" else None
    repo_path = pick.get("path") if pick.get("source") == "github" else None
    data = load_comparison_json(
        local_path=local_path,
        github_settings=gh_settings,
        repo_path=repo_path,
    )
    if not data:
        st.error("Could not load comparison file.")
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paired personas", int(data.get("n_paired", 0)))
    c2.metric("Accuracy A", pct(100 * float(data.get("accuracy_a", 0))))
    c3.metric("Accuracy B", pct(100 * float(data.get("accuracy_b", 0))))
    ate = float(data.get("ate_b_minus_a_pp", 0))
    c4.metric("ATE (B − A)", f"{ate:+.1f} pp")

    if data.get("significant_at_0_05"):
        insight(
            f"<strong>Significant at α=0.05</strong> — p = {float(data.get('mcnemar_p_value', 0)):.4f}"
        )
    else:
        st.caption(f"Not significant at α=0.05 (p = {float(data.get('mcnemar_p_value', 0)):.4f})")

    left, right = st.columns(2)
    with left:
        st.subheader("Summary")
        st.dataframe(comparison_summary_df(data), hide_index=True, use_container_width=True)
    with right:
        st.subheader("2×2 contingency (counts)")
        table = data.get("mcnemar_table", {})
        cells = table.get("cells", [[0, 0], [0, 0]])
        fig = px.imshow(
            cells,
            text_auto=True,
            x=[f"{data.get('name_b', 'B')} correct", f"{data.get('name_b', 'B')} wrong"],
            y=[f"{data.get('name_a', 'A')} correct", f"{data.get('name_a', 'A')} wrong"],
            color_continuous_scale=[[0, BRAND["light_blue"]], [1, BRAND["navy"]]],
        )
        chart_layout(fig, height=360)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Discordant breakdown")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Both correct", int(data.get("both_correct", 0)))
    d2.metric("Both wrong", int(data.get("both_wrong", 0)))
    d3.metric("A only correct", int(data.get("a_only_correct", 0)))
    d4.metric("B only correct", int(data.get("b_only_correct", 0)))

    if not mcnemar.empty and "Note" not in mcnemar.columns:
        with st.expander("All comparisons (CSV export)"):
            st.dataframe(mcnemar, use_container_width=True, hide_index=True)


def page_test_cases(cases: pd.DataFrame, personas: pd.DataFrame) -> None:
    hero("User Test Cases", "Source workbook with truth labels from evaluation runs")

    if cases.empty:
        st.info("No test cases loaded.")
        return

    pid = st.selectbox(
        "Persona",
        ["(all)"] + sorted(cases["persona_id"].dropna().astype(str).unique().tolist()),
    )
    df = cases if pid == "(all)" else cases[cases["persona_id"].astype(str) == pid].copy()

    if pid != "(all)" and not personas.empty and "Persona ID" in personas.columns:
        pr = personas[personas["Persona ID"].astype(str) == pid][
            ["Display Name", "Truth Label", "Predicted Label", "Correct Match"]
        ].drop_duplicates()
        if not pr.empty:
            st.subheader("Truth vs predicted (eval runs)")
            st.dataframe(pr, hide_index=True, use_container_width=True)

    key_cols = [
        c for c in [
            "persona_id",
            "engineered_for",
            "ix. final eligibility outcome",
            "ix. manual label",
            "simulated_user_message",
            "labeler notes",
        ]
        if c in df.columns
    ]
    st.subheader("Workbook truth columns")
    st.dataframe(df[key_cols] if key_cols else df, use_container_width=True, hide_index=True)
    with st.expander("All columns"):
        st.dataframe(df, use_container_width=True, hide_index=True)


# ── Runtime helpers ────────────────────────────────────────────────────────────

def _run_script(script: Path) -> None:
    if script.is_file():
        subprocess.run([sys.executable, str(script)], cwd=str(DESK), check=False)


def _is_streamlit_cloud() -> bool:
    return Path("/mount/src").exists() or bool(os.environ.get("STREAMLIT_SHARING_MODE"))


def _is_codespace() -> bool:
    return Path("/workspaces").exists() and bool(os.environ.get("CODESPACES"))


def _team_password_ok() -> None:
    pwd = ""
    try:
        pwd = st.secrets.get("TEAM_PASSWORD", "")
    except Exception:
        pwd = os.environ.get("TEAM_PASSWORD", "")
    if not pwd or st.session_state.get("team_auth"):
        return
    hero("AFW Eval Dashboard", "Enter team password to continue")
    entered = st.text_input("Password", type="password")
    if st.button("Continue", type="primary") and entered == pwd:
        st.session_state.team_auth = True
        st.rerun()
    st.stop()


def _load_tables() -> dict[str, pd.DataFrame]:
    cloud = _is_streamlit_cloud()
    codespace = _is_codespace()
    local_ok = _has_local_export()
    secrets_obj = getattr(st, "secrets", None)
    try:
        _ = st.secrets
        secrets_obj = st.secrets
    except Exception:
        pass
    gh_settings = resolve_github_settings(
        secrets=secrets_obj,
        config_path=None if cloud else CONFIG,
    )

    if cloud and local_ok:
        use_github = False
        st.sidebar.success("Data: committed in repo")
    elif cloud or (gh_settings and not (codespace and local_ok)):
        use_github = True
        st.sidebar.success(f"Data: github.com/{gh_settings['owner']}/{gh_settings['repo']}")
    elif local_ok:
        use_github = st.sidebar.radio("Data source", ["Local", "GitHub"], index=0) == "GitHub"
    else:
        use_github = True

    if use_github:
        if not gh_settings:
            st.error("GitHub not configured.")
            st.stop()
        tables = load_tables_github(
            f"{gh_settings['owner']}/{gh_settings['repo']}:{gh_settings['branch']}",
            use_config_file=not cloud,
        )
        if tables["runs"].empty:
            st.error("Could not load data from GitHub.")
            st.stop()
    else:
        root = Path(st.sidebar.text_input("Data folder", str(_find_data_root())))
        if st.sidebar.button("Sync from GitHub"):
            load_tables_local.clear()
            _run_script(DESK / "sync_powerbi_from_github.py")
            st.rerun()
        tables = load_tables_local(str(root), _data_fingerprint(root))

    tables["personas"] = prepare_personas(tables["personas"])
    return tables


def render_dashboard() -> None:
    inject_css()
    _team_password_ok()

    logo_candidates = [
        DESK / "afw_eval_agent_ui" / "assets" / "afw_logo.png",
        DESK / "assets" / "afw_logo.png",
    ]
    logo = next((p for p in logo_candidates if p.is_file()), None)
    if logo:
        st.sidebar.image(str(logo), width=100)
    st.sidebar.markdown("### AFW Eval")
    st.sidebar.caption("Angel Flight West · UC Davis GSM MSBA")

    if st.sidebar.toggle("Auto-refresh (20 min)", value=True):
        st.markdown('<meta http-equiv="refresh" content="1200">', unsafe_allow_html=True)

    tables = _load_tables()
    runs = tables["runs"]
    personas = tables["personas"]
    turns = tables["turns"]
    summary = tables["summary"]
    mcnemar = tables["mcnemar"]
    cases = tables["cases"]
    refresh = tables["refresh"]

    if not refresh.empty and "Last Updated UTC" in refresh.columns:
        st.sidebar.caption(f"Last export: {refresh['Last Updated UTC'].iloc[0]}")
    if "meta" in tables and not tables["meta"].empty and "run_count" in tables["meta"].columns:
        st.sidebar.metric("Runs", int(tables["meta"]["run_count"].iloc[0]))

    st.sidebar.markdown("---")
    run_options = sorted(runs["Display Name"].dropna().unique()) if not runs.empty else []
    selected_labels = st.sidebar.multiselect(
        "Filter arms",
        run_options,
        default=run_options,
        help="Power BI guide: slicer on arm / display name",
    )
    selected_ids = (
        runs[runs["Display Name"].isin(selected_labels)]["Run ID"].tolist()
        if not runs.empty and selected_labels
        else None
    )
    runs, personas, turns, summary = filter_runs(
        runs, personas, turns, summary, selected_ids
    )

    st.sidebar.markdown(
        "[GitHub repo](https://github.com/shprasa/afw-chatbot-eval-agent) · Public"
    )

    gh_for_mcn = resolve_github_settings(
        secrets=getattr(st, "secrets", None),
        config_path=None if _is_streamlit_cloud() else CONFIG,
    )
    workspace_root = DESK / "workspace"
    if not (workspace_root / "comparisons").is_dir():
        workspace_root = DESK / "AFW_Eval_Agent_Handoff" / "workspace"

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Run Overview",
        "Accuracy by Class",
        "Confusion",
        "Failure Review",
        "Conversations",
        "McNemar's Test",
        "User Test Cases",
    ])

    with tab1:
        page_run_overview(runs, personas)
    with tab2:
        page_accuracy_by_class(summary, runs)
    with tab3:
        page_confusion(personas)
    with tab4:
        page_failure_review(personas, turns)
    with tab5:
        page_conversations(turns, personas)
    with tab6:
        page_mcnemar_test(mcnemar, gh_for_mcn, workspace_root)
    with tab7:
        page_test_cases(cases, personas)


def main() -> None:
    st.set_page_config(
        page_title="AFW Eval Dashboard",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_dashboard()


if __name__ == "__main__":
    main()
else:
    render_dashboard()
