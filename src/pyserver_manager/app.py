from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ManagerConfig, load_config
from .menu import prompt_action
from .runner import CommandRunner

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "apps.yaml"


class ManagerApp:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.project_root = config_path.parent.resolve()
        self.runner = CommandRunner(self.project_root)
        self._config: ManagerConfig | None = None

    def run(self) -> None:
        while True:
            if not self._config:
                if not self._load_config():
                    return

            selection = prompt_action(self._config.apps)
            if selection == "exit":
                print("Goodbye!")
                return
            if selection == "reload":
                print("Reloading configuration...")
                if not self._load_config(force=True) and self._config is None:
                    print("Unable to continue without a valid configuration. Exiting.")
                    return
                continue

            self.runner.run(selection)

    def _load_config(self, force: bool = False) -> bool:
        try:
            self._config = load_config(self.config_path)
            return True
        except Exception as exc:  # noqa: BLE001 - show the error to the user
            print(f"Failed to load configuration: {exc}")
            if self._config and force:
                print("Keeping previous configuration. Press Enter to return to the menu.")
                input()
                return True
            input("Press Enter to exit...")
            return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interactive manager for lab applications.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the apps configuration file (YAML).",
    )
    args = parser.parse_args(argv)

    app = ManagerApp(args.config)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
