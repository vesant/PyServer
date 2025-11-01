from __future__ import annotations

from typing import Iterable, List
import os

from .config import AppDefinition

MENU_SEPARATOR = "=" * 60


def prompt_action(apps: Iterable[AppDefinition]) -> AppDefinition | str:
    """Show the menu and return the chosen action.

    Returns an AppDefinition when the user selects an app, or the strings
    "reload" / "exit" for the auxiliary actions.
    """

    app_list: List[AppDefinition] = list(apps)

    def clear_screen() -> None:
        """Clear the terminal screen in a cross-platform way."""
        # Windows uses 'cls', Unix-like systems use 'clear'
        os.system("cls" if os.name == "nt" else "clear")

    aux_offset = len(app_list) + 1
    reload_idx = aux_offset
    clear_idx = aux_offset + 1
    exit_idx = aux_offset + 2

    def print_menu() -> None:
        print(MENU_SEPARATOR)
        print("PyServer Manager")
        print(MENU_SEPARATOR)
        for index, app in enumerate(app_list, start=1):
            details = f" - {app.description}" if app.description else ""
            print(f"{index}. {app.name}{details}")
        print(f"{reload_idx}. Reload configuration")
        print(f"{clear_idx}. Clear screen")
        print(f"{exit_idx}. Exit")
        print(MENU_SEPARATOR)

    print_menu()

    while True:
        try:
            raw_choice = input("Select an option: ").strip()
            choice = int(raw_choice)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if 1 <= choice <= len(app_list):
            return app_list[choice - 1]
        if choice == reload_idx:
            return "reload"
        if choice == clear_idx:
            clear_screen()
            print_menu()
            continue
        if choice == exit_idx:
            return "exit"

        print("Choice out of range. Try again.")
