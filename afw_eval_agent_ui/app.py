"""Live Streamlit front-end for the AFW Screening Chatbot Evaluation Agent."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from afw_eval_agent.config import AGENT_ROOT, Workspace, default_workspace
from afw_eval_agent.github_publish import publish_workspace, resolve_credentials
from afw_eval_agent.mcnemar import compute_mcnemar, write_comparison_outputs
from afw_eval_agent.powerbi_export import export_powerbi_data
from afw_eval_agent.registry import list_models, list_prompt_labels
from afw_eval_agent.runner import run_evaluation
from afw_eval_agent.template import detect_sheet, validate_workbook
from afw_eval_agent.wizard import bootstrap_workspace
from afw_eval_dashboard.theme import BRAND, inject_css

LOGO_CANDIDATES = [
    ROOT / "afw_eval_agent_ui" / "assets" / "afw_logo.png",
    ROOT / "assets" / "afw_logo.png",
]


def _logo_path() -> Path | None:
    for p in LOGO_CANDIDATES:
        if p.is_file():
            return p
    return None


def _workspace() -> Workspace:
    ws = Workspace(default_workspace())
    ws.ensure_dirs()
    bootstrap_workspace(ws)
    return ws


def _save_to_github(ws: Workspace) -> None:
    creds = resolve_credentials(secrets=getattr(st, "secrets", None))
    if not creds:
        st.error("Unable to save results. Contact the AFW platform administrator.")
        return
    with st.spinner("Pushing workspace files to GitHub…"):
        result = publish_workspace(ws, message="Eval agent: save workspace to repo")
    st.success(f"Saved **{result['count']}** files to [{result['repo']}]({result['url']}).")
    st.caption("Dashboard refreshes within ~20 minutes (or reload the page).")


def render_agent() -> None:
    inject_css()
    col_l, col_t = st.columns([1, 4])
    with col_l:
        logo = _logo_path()
        if logo:
            st.image(str(logo), width=110)
        else:
            st.markdown("### ✈️")
    with col_t:
        st.markdown(
            f"<h2 style='color:{BRAND['navy']};margin:0'>AFW Screening Eval Agent</h2>"
            f"<p style='color:{BRAND['muted_teal']}'>Angel Flight West · UC Davis GSM MSBA · Live hosted agent</p>",
            unsafe_allow_html=True,
        )

    ws = _workspace()
    tab_run, tab_mcn, tab_runs = st.tabs(["Run evaluation", "McNemar comparison", "Saved runs"])

    with tab_run:
        st.subheader("New evaluation run")
        datasets = sorted(ws.datasets.glob("*.xlsx")) if ws.datasets.is_dir() else []
        if not datasets:
            st.warning("No datasets in `workspace/datasets/`. Add an Excel workbook first.")
        else:
            ds_names = [d.name for d in datasets]
            ds_pick = st.selectbox("Persona workbook", ds_names)
            dataset = ws.datasets / ds_pick
            sheet = detect_sheet(dataset)
            _, issues = validate_workbook(dataset, sheet)
            if issues:
                st.warning("Workbook validation issues: " + "; ".join(issues[:3]))

            models = list_models()
            model_key = st.selectbox(
                "Model host",
                list(models.keys()),
                format_func=lambda k: models[k]["display"],
            )
            prompts = list_prompt_labels()
            prompt_key = st.selectbox(
                "Prompt label",
                list(prompts.keys()),
                format_func=lambda k: prompts[k]["label"],
            )
            run_label = st.text_input("Run label", value="eval_run")
            c1, c2, c3 = st.columns(3)
            resume = c1.checkbox("Resume incomplete run")
            limit = c2.number_input("Persona limit (0 = all)", min_value=0, value=0, step=1)
            workers = c3.number_input("Parallel workers", min_value=1, max_value=12, value=6)

            if st.button("Start evaluation", type="primary"):
                if not (AGENT_ROOT / "chatbot_live_eval.py").is_file():
                    st.error("chatbot_live_eval.py not found in repo root.")
                else:
                    with st.status("Running live evaluation…", expanded=True) as status:
                        try:
                            entry = run_evaluation(
                                workspace=ws,
                                model_key=model_key,
                                prompt_key=prompt_key,
                                prompt_label=prompts[prompt_key]["label"],
                                prompt_file=None,
                                dataset_xlsx=dataset,
                                dataset_sheet=sheet,
                                run_label=run_label,
                                resume=resume,
                                eval_limit=int(limit) if limit else None,
                                parallel_workers=int(workers),
                            )
                            status.update(label="Evaluation complete", state="complete")
                            st.session_state["last_run_id"] = entry["run_id"]
                            st.success(f"Run saved: `{entry['run_id']}`")
                        except Exception as exc:
                            status.update(label="Evaluation failed", state="error")
                            st.exception(exc)

            if st.session_state.get("last_run_id"):
                st.info(f"Last run: **{st.session_state['last_run_id']}**")
                if st.button("Save this eval to GitHub repo"):
                    _save_to_github(ws)

    with tab_mcn:
        st.subheader("Compare two runs (McNemar)")
        runs = ws.load_manifest()
        if len(runs) < 2:
            st.info("Need at least two completed runs.")
        else:
            labels = [r.get("display_name", r["run_id"]) for r in runs]
            idx_a = st.selectbox("Group A", range(len(labels)), format_func=lambda i: labels[i])
            idx_b = st.selectbox("Group B", range(len(labels)), index=min(1, len(labels) - 1), format_func=lambda i: labels[i])
            if st.button("Run McNemar test", type="primary"):
                run_a, run_b = runs[idx_a], runs[idx_b]
                with st.spinner("Computing McNemar…"):
                    stats = compute_mcnemar(
                        run_a["predictions_csv"],
                        run_b["predictions_csv"],
                        run_a.get("display_name", run_a["run_id"]),
                        run_b.get("display_name", run_b["run_id"]),
                        agent_root=AGENT_ROOT,
                    )
                    write_comparison_outputs(stats, ws.comparisons)
                    export_powerbi_data(ws)
                st.success("McNemar outputs saved to `workspace/comparisons/`.")
                st.session_state["last_mcnemar"] = f"{labels[idx_a]} vs {labels[idx_b]}"
            if st.session_state.get("last_mcnemar"):
                st.info(f"Last comparison: **{st.session_state['last_mcnemar']}**")
                if st.button("Save McNemar results to GitHub repo"):
                    _save_to_github(ws)

    with tab_runs:
        runs = ws.load_manifest()
        if not runs:
            st.info("No runs yet.")
        else:
            for r in runs:
                with st.expander(r.get("display_name", r["run_id"]), expanded=False):
                    st.write(f"**Created:** {r.get('created_utc', '')}")
                    st.write(f"**API:** {r.get('api_base_url', '')}")
                    st.write(f"**Prompt:** {r.get('prompt_label', '')}")
                    st.write(f"**Predictions:** `{r.get('predictions_csv', '')}`")

        if st.button("Refresh dashboard export only"):
            export_powerbi_data(ws)
            st.success("Export refreshed.")
        if st.button("Save all workspace outputs to GitHub repo"):
            _save_to_github(ws)


def main() -> None:
    render_agent()


if __name__ == "__main__":
    main()
else:
    render_agent()
