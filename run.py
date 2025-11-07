#!/usr/bin/env python3
"""Cross-platform launcher that picks the repository virtualenv (if present)
and runs the pyserver_manager app module.

Usage:
  python run.py [--dry-run] [--config PATH] [-- <extra args>]

Options:
  --dry-run    Print the chosen python executable and command, then exit.
  --config     Path to an apps.yaml config (forwarded to the app module).

Behavior:
  - Looks for virtualenv folders in the project root: .venv, venv, env
  - Chooses the appropriate python executable for the detected OS
  - Falls back to the currently-running interpreter if no venv found
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional


def find_venv_python(root: Path) -> Optional[Path]:
    """Search common venv directories and return the python executable path.

    Looks for (in order): .venv, venv, env
    """
    candidates = [root / ".venv", root / "venv", root / "env"]
    for cand in candidates:
        if not cand.exists():
            continue
        # Platform-specific location
        if os.name == "nt":
            p = cand / "Scripts" / "python.exe"
        else:
            p = cand / "bin" / "python"
        if p.exists():
            return p
    return None


def build_command(python: Path, extra: Iterable[str]) -> List[str]:
    cmd = [str(python), "-m", "pyserver_manager.app"]
    cmd.extend(extra)
    return cmd


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launcher for pyserver_manager")
    parser.add_argument("--dry-run", action="store_true", help="Show the command and exit")
    parser.add_argument("--config", type=str, help="Path to a custom apps.yaml (forwarded)")
    parser.add_argument("--check", action="store_true", help=argparse.SUPPRESS)
    # capture any remaining args and forward them to the manager
    parser.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args forwarded to the manager")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    project_root = Path(__file__).resolve().parent

    venv_python = find_venv_python(project_root)
    if venv_python:
        python_to_use = venv_python
    else:
        python_to_use = Path(sys.executable)

    # Build forward args: include --config if provided, and any extras
    forward: List[str] = []
    if args.config:
        forward.extend(["--config", args.config])
    if args.extra:
        # args.extra includes the leading '--' if used; keep as-is
        forward.extend(args.extra)

    cmd = build_command(python_to_use, forward)

    # Ensure the child process can import the package in `src/` by setting PYTHONPATH.
    env = os.environ.copy()
    src_path = str(project_root / "src")
    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = src_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = src_path

    if args.dry_run or args.check:
        print("Selected python:", python_to_use)
        print("Command:", " ".join(cmd))
        print("PYTHONPATH:", env.get("PYTHONPATH"))
        return 0

    try:
        return subprocess.call(cmd, env=env)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
