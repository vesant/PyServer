from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Dict

from .config import AppDefinition


class CommandRunner:
    """Run app commands inside the manager process."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def run(self, app: AppDefinition) -> None:
        working_dir = app.resolved_working_dir(self.project_root)
        env = self._build_environment(app.environment)

        os.system("cls" if os.name == "nt" else "clear")
        print(f"→ Starting '{app.name}' in {working_dir}...")
        print("→ Press Ctrl+C to stop the command and return to the menu.\n")

        process = subprocess.Popen(
            app.command,
            cwd=working_dir,
            env=env,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        assert process.stdout is not None

        try:
            for line in process.stdout:
                print(line, end="")
            exit_code = process.wait()
        except KeyboardInterrupt:
            print("\n→ Stopping command...")
            _graceful_terminate(process)
            exit_code = process.wait()
        finally:
            process.stdout.close()

        if exit_code == 0:
            print(f"\n→ '{app.name}' exited cleanly. Press Enter to return to the menu.")
        else:
            print(
                f"\n→ '{app.name}' exited with code {exit_code}."
                " Review the output above and press Enter to return to the menu."
            )
        input()

    def _build_environment(self, overrides: Dict[str, str]) -> Dict[str, str]:
        env = os.environ.copy()
        env.update(overrides)
        return env


def _graceful_terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    if sys.platform != "win32":
        try:
            process.send_signal(signal.SIGINT)
            return
        except Exception:
            pass
    process.terminate()
