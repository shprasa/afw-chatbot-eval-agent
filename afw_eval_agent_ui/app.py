"""Live Streamlit front-end for the AFW Screening Chatbot Evaluation Agent."""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from afw_eval_agent.background_job import (
    job_is_active,
    job_log_path,
    job_state_path,
    load_job_state,
    read_job_log_tail,
    start_background_evaluation,
    sync_job_state,
)
from afw_eval_agent.config import AGENT_ROOT, Workspace, default_workspace
from afw_eval_agent.github_publish import publish_file, publish_workspace, repo_relative_path, resolve_credentials
from afw_eval_agent.mcnemar import compute_mcnemar, write_comparison_outputs
from afw_eval_agent.powerbi_export import export_powerbi_data
from afw_eval_agent.registry import add_model, add_prompt_label, list_models, list_prompt_labels
from afw_eval_agent.template import create_template, detect_sheet, validate_workbook
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


def _ensure_template(ws: Workspace) -> Path:
    tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
    if not tpl.is_file():
        create_template(tpl)
    return tpl


def _list_datasets(ws: Workspace) -> list[Path]:
    ws.datasets.mkdir(parents=True, exist_ok=True)
    return sorted(ws.datasets.glob("*.xlsx"), key=lambda p: p.name.lower())


def _save_dataset_upload(ws: Workspace, uploaded) -> Path:
    dest = ws.datasets / uploaded.name
    dest.write_bytes(uploaded.getvalue())
    return dest


def _push_dataset_to_repo(ws: Workspace, local: Path) -> bool:
    return publish_file(
        local,
        repo_relative_path(ws, local),
        message="Eval agent: upload persona workbook",
        secrets=getattr(st, "secrets", None),
    )


def _clear_job_files(ws: Workspace) -> None:
    for path in (job_state_path(ws), job_log_path(ws)):
        if path.is_file():
            path.unlink()


def _save_to_github(ws: Workspace) -> None:
    creds = resolve_credentials(secrets=getattr(st, "secrets", None))
    if not creds:
        st.error("Unable to save results. Contact the AFW platform administrator.")
        return
    with st.spinner("Pushing workspace files to GitHub…"):
        result = publish_workspace(ws, message="Eval agent: save workspace to repo")
    st.success(f"Saved **{result['count']}** files to [{result['repo']}]({result['url']}).")
    st.caption("Dashboard refreshes within ~20 minutes (or reload the page).")


def _render_active_job_panel(ws: Workspace) -> bool:
    state = sync_job_state(ws)
    if not state:
        return False

    status = state.get("status", "")
    with st.container(border=True):
        st.markdown("### Evaluation status")
        if status in {"pending", "running"}:
            st.warning(
                f"**In progress:** {state.get('run_label', 'eval')} · "
                f"{state.get('dataset', '')} · "
                "You can switch tabs or pages — this run continues in the background."
            )
        elif status == "completed":
            st.success(
                f"**Completed:** `{state.get('result_run_id', '')}` · "
                f"{state.get('run_label', '')}"
            )
            if state.get("email_status"):
                st.caption(state["email_status"])
            st.session_state["last_run_id"] = state.get("result_run_id")
        elif status == "failed":
            st.error(f"**Failed:** {state.get('error', 'Unknown error')}")
            if state.get("email_status"):
                st.caption(state["email_status"])

        total = max(int(state.get("total") or 0), 1)
        completed = min(int(state.get("completed") or 0), total)
        remaining = max(int(state.get("remaining") or 0), 0)
        in_flight = int(state.get("in_flight") or 0)

        if status in {"pending", "running", "completed"}:
            st.progress(
                completed / total if status != "completed" else 1.0,
                text=f"{completed} / {total} personas complete",
            )
            bits = [f"**{completed}** completed", f"**{remaining}** remaining", f"**{total}** total"]
            if in_flight and status in {"pending", "running"}:
                bits.insert(1, f"**{in_flight}** in progress")
            hint = ""
            if status in {"pending", "running"} and completed == 0 and in_flight:
                hint = (
                    " First completion often takes **1–3 minutes** "
                    "(multiple API turns per persona)."
                )
            st.caption(" · ".join(bits) + hint)

        st.markdown("**Live session log**")
        log_text = read_job_log_tail(ws)
        st.code(log_text or "Waiting for log output…", language=None)

        if status in {"completed", "failed"}:
            if st.button("Clear evaluation status", key="clear_job_status"):
                _clear_job_files(ws)
                st.rerun()

    return job_is_active(state)


@st.fragment(run_every=timedelta(seconds=5))
def _poll_active_job(ws: Workspace) -> None:
    if job_is_active(sync_job_state(ws)):
        _render_active_job_panel(ws)


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
            f"<h2 style='color:{BRAND['navy']};margin:0'>AFW Screening Chatbot Evaluation Agent</h2>"
            f"<p style='color:{BRAND['muted_teal']}'>Angel Flight West · UC Davis GSM MSBA · Live hosted agent</p>",
            unsafe_allow_html=True,
        )

    ws = _workspace()
    tab_run, tab_mcn, tab_runs = st.tabs(["Run evaluation", "McNemar comparison", "Saved runs"])

    with tab_run:
        job_running = _render_active_job_panel(ws)
        if job_running:
            _poll_active_job(ws)

        st.subheader("New evaluation run")
        template_path = _ensure_template(ws)

        st.markdown("**Persona workbook**")
        st.info(
            "**Using your own workbook — required steps**\n\n"
            "1. Download the template and fill in your personas.\n"
            "2. Upload your `.xlsx` file.\n"
            "3. Click **Save uploaded workbook** and wait for confirmation.\n"
            "4. **Select your saved workbook** from the **Persona workbook** dropdown below.\n"
            "5. Only then click **Start evaluation**.\n\n"
            "If you skip step 3 or 4, the run will use whichever workbook is currently "
            "selected in the dropdown — not the file you just uploaded."
        )

        dl_col, _ = st.columns([1, 2])
        with dl_col:
            st.download_button(
                "Download template (.xlsx)",
                data=template_path.read_bytes(),
                file_name="AFW_Eval_Test_Cases_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Required column layout for persona test cases",
            )

        uploaded_wb = st.file_uploader(
            "Upload persona workbook (.xlsx)",
            type=["xlsx"],
            help="Must match the template column layout exactly.",
        )
        if uploaded_wb is not None and st.button("Save uploaded workbook", key="save_uploaded_wb"):
            dest = _save_dataset_upload(ws, uploaded_wb)
            sheet = detect_sheet(dest)
            _, issues = validate_workbook(dest, sheet)
            if issues:
                st.error("Workbook validation failed: " + "; ".join(issues[:5]))
            else:
                if _push_dataset_to_repo(ws, dest):
                    st.success(
                        f"Saved **`{uploaded_wb.name}`** to the repo. "
                        "It is now selected in the dropdown below — confirm before starting."
                    )
                else:
                    st.success(
                        f"Saved **`{uploaded_wb.name}`** locally. "
                        "It is now selected in the dropdown below — confirm before starting."
                    )
                st.session_state["eval_dataset_pick"] = uploaded_wb.name
                st.rerun()

        datasets = _list_datasets(ws)
        if not datasets:
            st.warning(
                "No persona workbooks in `workspace/datasets/` yet. "
                "Download the template, fill it in, upload, and save before running."
            )
        else:
            ds_names = [d.name for d in datasets]
            pick_default = st.session_state.get("eval_dataset_pick")
            pick_index = ds_names.index(pick_default) if pick_default in ds_names else 0
            ds_pick = st.selectbox(
                "Persona workbook (select the saved file you will run)",
                ds_names,
                index=pick_index,
                key="eval_dataset_pick",
            )
            dataset = ws.datasets / ds_pick
            sheet = detect_sheet(dataset)
            _, issues = validate_workbook(dataset, sheet)
            if issues:
                st.warning("Workbook validation issues: " + "; ".join(issues[:3]))

            models = list_models()
            model_keys = list(models.keys())
            model_key = st.selectbox(
                "Model host",
                model_keys,
                format_func=lambda k: models[k]["display"],
                key="eval_model_host",
            )
            with st.expander("Add new model host"):
                st.caption(
                    "Register another chatbot API endpoint. "
                    "The prompt must already be deployed on that host."
                )
                new_model_display = st.text_input(
                    "Display name",
                    placeholder="e.g. OpenAI staging host",
                    key="new_model_display",
                )
                new_model_url = st.text_input(
                    "Base URL",
                    placeholder="https://my-host.azurewebsites.net",
                    key="new_model_url",
                )
                if st.button("Save model host", key="save_model_host"):
                    if not new_model_display.strip() or not new_model_url.strip():
                        st.error("Display name and Base URL are required.")
                    else:
                        try:
                            added_key = add_model(
                                display=new_model_display.strip(),
                                base_url=new_model_url.strip(),
                                backend="",
                            )
                            st.session_state["eval_model_host"] = added_key
                            st.success(
                                f"Added model host **{new_model_display.strip()}**. "
                                "Click **Save to GitHub repo** after your run to share with the team."
                            )
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))

            prompts = list_prompt_labels()
            prompt_keys = list(prompts.keys())
            prompt_key = st.selectbox(
                "Prompt label",
                prompt_keys,
                format_func=lambda k: prompts[k]["label"],
                key="eval_prompt_label",
            )
            with st.expander("Add new prompt label"):
                st.caption(
                    "Tag which system prompt version is live on the API backend. "
                    "You do not upload prompt text here."
                )
                new_prompt_label = st.text_input(
                    "Label text",
                    placeholder="e.g. System Prompt v12 — March deploy",
                    key="new_prompt_label",
                )
                new_prompt_notes = st.text_input(
                    "Notes (optional)",
                    placeholder="Deploy date, ticket, etc.",
                    key="new_prompt_notes",
                )
                if st.button("Save prompt label", key="save_prompt_label"):
                    if not new_prompt_label.strip():
                        st.error("Label text is required.")
                    else:
                        try:
                            added_key = add_prompt_label(
                                label=new_prompt_label.strip(),
                                notes=new_prompt_notes.strip(),
                            )
                            st.session_state["eval_prompt_label"] = added_key
                            st.success(
                                f"Added prompt label **{new_prompt_label.strip()}**. "
                                "Click **Save to GitHub repo** after your run to share with the team."
                            )
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))

            run_label = st.text_input("Run label", value="eval_run")
            notify_email = st.text_input(
                "Email for completion notification (optional)",
                placeholder="you@example.com",
                key="eval_notify_email",
                help="You will receive an email when the evaluation finishes or fails.",
            )
            c1, c2, c3 = st.columns(3)
            resume = c1.checkbox("Resume incomplete run")
            limit = c2.number_input("Persona limit (0 = all)", min_value=0, value=0, step=1)
            workers = c3.number_input("Parallel workers", min_value=1, max_value=12, value=6)

            if job_running:
                st.caption("An evaluation is already running. See **Evaluation status** above.")

            if st.button(
                "Start evaluation",
                type="primary",
                disabled=job_running,
            ):
                if not (AGENT_ROOT / "chatbot_live_eval.py").is_file():
                    st.error("chatbot_live_eval.py not found in repo root.")
                else:
                    try:
                        start_background_evaluation(
                            ws,
                            model_key=model_key,
                            prompt_key=prompt_key,
                            prompt_label=prompts[prompt_key]["label"],
                            dataset_xlsx=dataset,
                            dataset_sheet=sheet,
                            run_label=run_label,
                            resume=resume,
                            eval_limit=int(limit) if limit else None,
                            parallel_workers=int(workers),
                            notify_email=notify_email,
                        )
                        st.success(
                            "Evaluation started in the background. "
                            "You can stay on this tab or switch to the Dashboard — "
                            "progress is shown under **Evaluation status**."
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

            last_id = st.session_state.get("last_run_id") or (
                load_job_state(ws) or {}
            ).get("result_run_id")
            if last_id:
                st.info(f"Last completed run: **{last_id}**")
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
            idx_b = st.selectbox(
                "Group B",
                range(len(labels)),
                index=min(1, len(labels) - 1),
                format_func=lambda i: labels[i],
            )
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
