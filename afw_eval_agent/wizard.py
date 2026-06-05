"""Interactive plug-and-play CLI for the AFW evaluation agent."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .config import AGENT_ROOT, Workspace, default_workspace
from .mcnemar import compute_mcnemar, write_comparison_outputs
from .presets import MODEL_CHOICES, PROMPT_CHOICES
from .runner import import_legacy_run, run_evaluation
from .template import create_template, detect_sheet, validate_workbook


def bootstrap_workspace(ws: Workspace) -> None:
    """Seed templates and default dataset on first use."""
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
    print("\n=== AFW Chatbot Evaluation Agent ===\n")
    print("All runs, reports, and comparisons are saved under workspace/ in this repo.")
    print("Commit and push workspace/ to GitHub after each eval.\n")
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


def _pick_dataset(ws: Workspace) -> tuple[Path, str]:
    print("\nTest cases workbook:")
    print("  1. Use file in workspace/datasets/")
    print("  2. Upload/copy path to a new workbook")
    print("  3. Create blank Excel template")
    choice = _prompt("Choice", "1")
    if choice == "3":
        tpl = ws.templates / "AFW_Eval_Test_Cases_Template.xlsx"
        create_template(tpl)
        dest = ws.datasets / "AFW_Eval_Test_Cases_Template.xlsx"
        shutil.copy2(tpl, dest)
        print(f"\nTemplate created:\n  {tpl}\n  {dest}")
        print("Fill in personas on sheet 'test_cases', then re-run this menu.")
        return dest, "test_cases"
    if choice == "2":
        src = Path(_prompt("Full path to Excel workbook"))
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
                return tpl, "test_cases"
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
    _, issues = validate_workbook(dataset, sheet)
    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"  - {issue}")
        if _prompt("Continue anyway? (y/N)", "n").lower() != "y":
            raise SystemExit("Fix workbook and retry.")
    return dataset, sheet


def menu_run_eval(ws: Workspace) -> None:
    dataset, sheet = _pick_dataset(ws)
    model_key = _choose(
        "Which API / model host?",
        [(k, v["display"]) for k, v in MODEL_CHOICES.items()],
    )
    prompt_key = _choose(
        "Which system prompt?",
        [(k, v["display"]) for k, v in PROMPT_CHOICES.items()]
        + [("custom", "Custom prompt file path")],
    )
    prompt_label = ""
    prompt_file: Path | None = None
    if prompt_key == "custom":
        prompt_label = _prompt("Label for this prompt (e.g. System Prompt v12)")
        p = Path(_prompt("Path to prompt .txt file"))
        if not p.is_file():
            raise FileNotFoundError(p)
        prompt_file = p
    else:
        prompt_label = PROMPT_CHOICES[prompt_key]["display"]
        rel = PROMPT_CHOICES[prompt_key]["prompt_file"]
        for candidate in (AGENT_ROOT / rel, AGENT_ROOT / "AFW_Eval_Agent_Handoff" / rel):
            if candidate.is_file():
                prompt_file = candidate
                break
    run_label = _prompt("Run label (short name for reports)", "eval_run")
    resume = _prompt("Resume incomplete run? (y/N)", "n").lower() == "y"
    limit_raw = _prompt("Limit personas (blank = all)", "")
    eval_limit = int(limit_raw) if limit_raw.isdigit() else None
    workers_raw = _prompt("Parallel workers", "6")
    workers = int(workers_raw) if workers_raw.isdigit() else 6

    entry = run_evaluation(
        workspace=ws,
        model_key=model_key,
        prompt_key=prompt_key if prompt_key != "custom" else "custom",
        prompt_label=prompt_label,
        prompt_file=prompt_file,
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
    pred_a = Path(run_a["predictions_csv"])
    pred_b = Path(run_b["predictions_csv"])
    name_a = run_a.get("display_name", run_a["run_id"])
    name_b = run_b.get("display_name", run_b["run_id"])
    stats = compute_mcnemar(pred_a, pred_b, name_a, name_b, agent_root=AGENT_ROOT)
    outputs = write_comparison_outputs(stats, ws.comparisons)
    print("\nMcNemar comparison saved:")
    for k, p in outputs.items():
        if p.exists():
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
        print(f"    Created: {r.get('created_utc', '')}")


def menu_import_legacy(ws: Workspace) -> None:
    print("\nImport an existing predictions CSV (e.g. from artifacts/) into the run manifest.")
    path = Path(_prompt("Path to chatbot_live_predictions*.csv"))
    display = _prompt("Display name for McNemar picker", path.stem)
    model_key = _choose(
        "Which API was this run?",
        [(k, v["display"]) for k, v in MODEL_CHOICES.items()],
    )
    prompt_label = _prompt("Prompt label", "System Prompt v1")
    entry = import_legacy_run(
        ws,
        path,
        display_name=display,
        model_key=model_key,
        prompt_label=prompt_label,
    )
    print(f"Imported as run: {entry['run_id']}")


def menu_set_workspace(ws: Workspace) -> Workspace:
    root = Path(_prompt("New workspace folder", str(ws.root)))
    ws = Workspace(root)
    cfg = ws.init_config_if_missing()
    cfg["workspace_root"] = str(root)
    ws.save_config(cfg)
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
        print("  4. Create / refresh Excel template")
        print("  5. Change workspace folder")
        print("  6. Import legacy predictions CSV")
        print("  7. Exit")
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
            elif choice == "5":
                ws = menu_set_workspace(ws)
            elif choice == "6":
                menu_import_legacy(ws)
            elif choice == "7":
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
