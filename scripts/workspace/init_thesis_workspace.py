#!/usr/bin/env python3
"""Copy the bundled thesis-ai-standard package into a project workspace."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
from pathlib import Path


def load_write_workflow_logs():
    module_path = Path(__file__).resolve().with_name("init_workflow_logs.py")
    spec = importlib.util.spec_from_file_location("init_workflow_logs", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load workflow log helper: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.write_workflow_logs


write_workflow_logs = load_write_workflow_logs()


def copytree_merge(src: Path, dst: Path, overwrite: bool) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Bundled template not found: {src}")

    if dst.exists() and not overwrite:
        raise FileExistsError(
            f"Target already exists: {dst}. Re-run with --overwrite to replace files."
        )

    if dst.exists() and overwrite:
        shutil.rmtree(dst)

    shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a thesis-ai-standard workspace from the chinese-thesis-workbench skill."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Project directory where thesis-ai-standard should be created.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing thesis-ai-standard directory.",
    )
    parser.add_argument(
        "--no-workflow-logs",
        action="store_true",
        help="Do not create paper-context/workflow markdown logs.",
    )
    parser.add_argument(
        "--overwrite-workflow-logs",
        action="store_true",
        help="Replace existing paper-context/workflow markdown logs.",
    )
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parents[2]
    src = skill_dir / "assets" / "thesis-ai-standard"
    target_dir = Path(args.target).resolve()
    dst = target_dir / "thesis-ai-standard"

    target_dir.mkdir(parents=True, exist_ok=True)
    copytree_merge(src, dst, overwrite=args.overwrite)
    written_logs = []
    if not args.no_workflow_logs:
        written_logs = write_workflow_logs(target_dir, overwrite=args.overwrite_workflow_logs)

    print(f"Initialized thesis workspace: {dst}")
    if not args.no_workflow_logs:
        print(f"Workflow logs: {target_dir / 'paper-context' / 'workflow'}")
        for path in written_logs:
            print(f"- {path}")
    print("Next files to fill:")
    if not args.no_workflow_logs:
        print(f"- {target_dir / 'paper-context' / 'workflow' / 'user-dashboard.md'}")
    print(f"- {dst / 'templates' / 'standard-profile.yaml'}")
    print(f"- {dst / 'templates' / 'thesis-ai-spec.yaml'}")
    print(f"- {dst / 'templates' / 'figure-registry.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
