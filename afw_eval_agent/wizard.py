"""Interactive CLI for the AFW Screening Chatbot Evaluation Agent."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .config import AGENT_ROOT, Workspace, default_workspace
from .mcnemar import compute_mcnemar, write_comparison_outputs
from .registry import (
    add_model,
    add_prompt_label,
    get_prompt_label,
    list_models,
    list_prompt_labels,
    load_registry,
)
from .runner import import_legacy_run, run_evaluation
from .template import (
    TEMPLATE_STRICT_NOTICE,
    create_template,
    detect_sheet,
    validate_workbook,
)

PRACTICUM_LINE = (
    "UC Davis Graduate School of Management MSBA — "
    "Angel Flight West Demand Management Practicum Team (2025–2026)"
)


def bootstrap_workspace(ws: Workspace) -> None:
    ws.ensure_dirs()
    tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
    if not tpl.is_file():
        create_template(tpl)
    bundled = AGENT_ROOT / "data" / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
    if not bundled.is_file():
        bundled = AGENT_ROOT / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
    if bundled.is_file():
        dest = ws.datasets / bundled.name
        if not dest.is_file():
            shutil.copy2(bundled, dest)
    load_registry()


def _prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{text}{suffix}: ").strip()
    return val or default


def _choose(prompt: str, options: list[tuple[str, str]]) -> str:
    print(f"\n{prompt}")
    for i, (key, label) in enumerate(options, 1):
        print(f"  {i}. {label}")
    while True:
        raw = input("Enter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print("Invalid choice — try again.")


def _resolve_workspace() -> Workspace:
    print("\n=== AFW Screening Chatbot Evaluation Agent ===\n")
    print(PRATICUM_LINE)
    print("\nAll runs, reports, and comparisons are saved under workspace/ in this repo.")
    print("Commit and push workspace/ and config/ to GitHub after changes.\n")
    default = default_workspace()
    root = Path(_prompt("Workspace folder (repo workspace/)", str(default)))
    ws = Workspace(root)
    cfg = ws.init_config_if_missing()
    if str(root) != cfg.get("workspace_root"):
        cfg["workspace_root"] = str(root)
        ws.save_config(cfg)
    bootstrap_workspace(ws)
    print(f"\nWorkspace ready: {ws.root}\n")
    return ws


def _validate_strict(dataset: Path, sheet: str, *, upload: bool) -> None:
    _, issues = validate_workbook(dataset, sheet)
    if issues:
        print("\nValidation failed — workbook does not match the required template:")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\n{TEMPLATE_STRICT_NOTICE}")
        if upload:
            raise SystemExit(
                "Fix your Excel file to match the template exactly, then upload again."
            )
        if _prompt("Continue anyway? (y/N)", "n").lower() != "y":
            raise SystemExit("Fix workbook and retry.")


def _pick_dataset(ws: Workspace) -> tuple[Path, str] | None:
    print("\nUser persona test cases (Excel):")
    print("  1. Use a file already in workspace/datasets/")
    print("  2. Upload your own Excel file (must match template EXACTLY)")
    print("  3. Create a blank template to fill in first")
    choice = _prompt("Choice", "1")

    if choice == "3":
        tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
        create_template(tpl)
        dest = ws.datasets / "AFW_Eval_Test_Cases_Template.xlsx"
        shutil.copy2(tpl, dest)
        print(f"\nTemplate created:\n  {tpl}\n  {dest}")
        print(TEMPLATE_STRICT_NOTICE)
        print("\nFill in personas on sheet 'test_cases', then re-run menu option 1.")
        return None

    strict_upload = choice == "2"
    if strict_upload:
        print(f"\n{TEMPLATE_STRICT_NOTICE}\n")
        src = Path(_prompt("Full path to your Excel workbook"))
        if not src.is_file():
            raise FileNotFoundError(src)
        dest = ws.datasets / src.name
        if src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        dataset = dest
    else:
        files = sorted(ws.datasets.glob("*.xlsx"))
        if not files:
            bundled = AGENT_ROOT / "data" / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
            if not bundled.is_file():
                bundled = AGENT_ROOT / "AFW_120_User_Test_Cases_Original_Style_Short.xlsx"
            if bundled.is_file():
                ws.datasets.mkdir(parents=True, exist_ok=True)
                dest = ws.datasets / bundled.name
                shutil.copy2(bundled, dest)
                files = [dest]
                print(f"Copied bundled 120-case dataset to {dest}")
            else:
                tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
                create_template(tpl)
                print(f"No datasets yet — template at {tpl}")
                print("Create or upload a dataset first (menu 4 or option 2).")
                return None
        if len(files) == 1:
            dataset = files[0]
            print(f"Using {dataset.name}")
        else:
            print("\nAvailable datasets:")
            for i, f in enumerate(files, 1):
                print(f"  {i}. {f.name}")
            idx = int(_prompt("Select dataset", "1")) - 1
            dataset = files[idx]

    sheet = detect_sheet(dataset)
    _validate_strict(dataset, sheet, upload=strict_upload)
    return dataset, sheet


def _pick_model(ws: Workspace) -> str:
    while True:
        models = list_models()
        options = [(k, v["display"]) for k, v in models.items()]
        options.append(("__add__", "Add a new API model host (saved to config/agent_registry.json)"))
        key = _choose("Which API / model host?", options)
        if key != "__add__":
            return key
        menu_add_model(ws)


def _pick_prompt_label(ws: Workspace) -> tuple[str, str]:
    print(
        "\nNote: The system prompt is deployed on the API backend only. "
        "You are selecting a LABEL to tag this run — not editing prompt text.\n"
    )
    while True:
        labels = list_prompt_labels()
        options = [(k, v["label"]) for k, v in labels.items()]
        options.append(("__add__", "Add a new prompt version label (saved to config/agent_registry.json)"))
        key = _choose("Which prompt version label?", options)
        if key == "__add__":
            menu_add_prompt_label(ws)
            continue
        meta = get_prompt_label(key)
        return key, meta["label"]


def menu_add_model(ws: Workspace) -> str:
    print("\nAdd API model host (saved to config/agent_registry.json — commit to GitHub).")
    display = _prompt("Display name (e.g. GPT-4o staging host)")
    base_url = _prompt("Base URL (e.g. https://my-host.azurewebsites.net)").rstrip("/")
    backend = _prompt("Backend type (openai or claude)", "openai")
    key = add_model(display=display, base_url=base_url, backend=backend)
    print(f"Saved model '{key}'. Commit config/agent_registry.json to share with the team.")
    return key


def menu_add_prompt_label(ws: Workspace) -> str:
    print("\nAdd prompt version LABEL (tags which backend prompt is live — you do not edit prompt text here).")
    label = _prompt("Label text (e.g. System Prompt v12 — March deploy)")
    notes = _prompt("Optional notes (deploy date, ticket, etc.)", "")
    key = add_prompt_label(label=label, notes=notes)
    print(f"Saved prompt label '{key}'. Commit config/agent_registry.json to reuse this label.")
    return key


def menu_run_eval(ws: Workspace) -> None:
    picked = _pick_dataset(ws)
    if picked is None:
        return
    dataset, sheet = picked
    model_key = _pick_model(ws)
    prompt_key, prompt_label = _pick_prompt_label(ws)
    run_label = _prompt("Run label (short name for reports)", "eval_run")
    resume = _prompt("Resume incomplete run? (y/N)", "n").lower() == "y"
    limit_raw = _prompt("Limit personas (blank = all)", "")
    eval_limit = int(limit_raw) if limit_raw.isdigit() else None
    workers_raw = _prompt("Parallel workers", "6")
    workers = int(workers_raw) if workers_raw.isdigit() else 6

    entry = run_evaluation(
        workspace=ws,
        model_key=model_key,
        prompt_key=prompt_key,
        prompt_label=prompt_label,
        prompt_file=None,
        dataset_xlsx=dataset,
        dataset_sheet=sheet,
        run_label=run_label,
        resume=resume,
        eval_limit=eval_limit,
        parallel_workers=workers,
    )
    print("\nRun complete. Saved to workspace:")
    print(f"  {ws.runs / entry['run_id']}")
    print(f"  Predictions: {entry['predictions_csv']}")
    print("\nCommit workspace/ and config/ after reviewing outputs.")


def menu_mcnemar(ws: Workspace) -> None:
    runs = ws.load_manifest()
    if len(runs) < 2:
        print("\nNeed at least two completed runs in workspace/runs/manifest.json")
        return
    print("\nCompleted runs:")
    for i, r in enumerate(runs, 1):
        print(f"  {i}. {r.get('display_name', r.get('run_id'))}")
    idx_a = int(_prompt("Select Group A", "1")) - 1
    idx_b = int(_prompt("Select Group B", "2")) - 1
    run_a, run_b = runs[idx_a], runs[idx_b]
    name_a = run_a.get("display_name", run_a["run_id"])
    name_b = run_b.get("display_name", run_b["run_id"])
    stats = compute_mcnemar(
        run_a["predictions_csv"],
        run_b["predictions_csv"],
        name_a,
        name_b,
        agent_root=AGENT_ROOT,
    )
    outputs = write_comparison_outputs(stats, ws.comparisons)
    print("\nMcNemar comparison saved:")
    for k, p in outputs.items():
        if Path(p).exists():
            print(f"  {k}: {p}")


def menu_list_runs(ws: Workspace) -> None:
    runs = ws.load_manifest()
    if not runs:
        print("\nNo runs yet.")
        return
    print(f"\n{len(runs)} run(s) in {ws.runs}:")
    for r in runs:
        print(f"  - {r.get('display_name', r['run_id'])}")
        print(f"    API: {r.get('api_base_url', '')}")
        print(f"    Prompt label: {r.get('prompt_label', '')}")
        print(f"    Created: {r.get('created_utc', '')}")


def menu_list_customization(ws: Workspace) -> None:
    print("\n--- Saved model hosts (config/agent_registry.json) ---")
    for k, m in list_models().items():
        tag = "builtin" if m.get("builtin") else "custom"
        print(f"  {k}: {m['display']} [{tag}]")
        print(f"       {m['base_url']}")
    print("\n--- Saved prompt labels (label only — prompt text is on API backend) ---")
    for k, p in list_prompt_labels().items():
        tag = "builtin" if p.get("builtin") else "custom"
        print(f"  {k}: {p['label']} [{tag}]")
        if p.get("notes"):
            print(f"       {p['notes']}")


def menu_import_legacy(ws: Workspace) -> None:
    print("\nImport an existing predictions CSV into the run manifest.")
    path = Path(_prompt("Path to chatbot_live_predictions*.csv"))
    display = _prompt("Display name for McNemar picker", path.stem)
    model_key = _pick_model(ws)
    prompt_key, prompt_label = _pick_prompt_label(ws)
    entry = import_legacy_run(
        ws,
        path,
        display_name=display,
        model_key=model_key,
        prompt_label=prompt_label,
    )
    print(f"Imported as run: {entry['run_id']} (prompt key: {prompt_key})")


def menu_set_workspace(ws: Workspace) -> Workspace:
    root = Path(_prompt("New workspace folder", str(ws.root)))
    ws = Workspace(root)
    cfg = ws.init_config_if_missing()
    cfg["workspace_root"] = str(root)
    ws.save_config(cfg)
    bootstrap_workspace(ws)
    print(f"Workspace set to {root}")
    return ws


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    ws = _resolve_workspace()
    if not (AGENT_ROOT / "chatbot_live_eval.py").is_file():
        print(f"ERROR: chatbot_live_eval.py not found in {AGENT_ROOT}")
        return 1

    while True:
        print("\n--- Main menu ---")
        print("  1. Run new evaluation")
        print("  2. Compare two runs (McNemar)")
        print("  3. List saved runs")
        print("  4. Create / refresh Excel template (strict format)")
        print("  5. Change workspace folder")
        print("  6. Import legacy predictions CSV")
        print("  7. Add API model host")
        print("  8. Add prompt version label")
        print("  9. List saved models and prompt labels")
        print(" 10. Exit")
        choice = _prompt("Choice", "1")
        try:
            if choice == "1":
                menu_run_eval(ws)
            elif choice == "2":
                menu_mcnemar(ws)
            elif choice == "3":
                menu_list_runs(ws)
            elif choice == "4":
                tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
                create_template(tpl)
                print(f"Template written: {tpl}")
                print(TEMPLATE_STRICT_NOTICE)
            elif choice == "5":
                ws = menu_set_workspace(ws)
            elif choice == "6":
                menu_import_legacy(ws)
            elif choice == "7":
                menu_add_model(ws)
            elif choice == "8":
                menu_add_prompt_label(ws)
            elif choice == "9":
                menu_list_customization(ws)
            elif choice == "10":
                print("Goodbye.")
                break
            else:
                print("Unknown option.")
        except KeyboardInterrupt:
            print("\nCancelled.")
        except Exception as exc:
            print(f"\nERROR: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
