from __future__ import annotations

from typing import Iterable, List

from .config import AppDefinition

MENU_SEPARATOR = "=" * 60


def prompt_action(apps: Iterable[AppDefinition]) -> AppDefinition | str:
    """Show the menu and return the chosen action.

    Returns an AppDefinition when the user selects an app, or the strings
    "reload" / "exit" for the auxiliary actions.
    """

    app_list: List[AppDefinition] = list(apps)

    print(MENU_SEPARATOR)
    print("PyServer Manager")
    print(MENU_SEPARATOR)
    for index, app in enumerate(app_list, start=1):
        details = f" - {app.description}" if app.description else ""
        print(f"{index}. {app.name}{details}")
    aux_offset = len(app_list) + 1
    print(f"{aux_offset}. Reload configuration")
    print(f"{aux_offset + 1}. Exit")
    print(MENU_SEPARATOR)

    while True:
        try:
            raw_choice = input("Select an option: ").strip()
            choice = int(raw_choice)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if 1 <= choice <= len(app_list):
            return app_list[choice - 1]
        if choice == aux_offset:
            return "reload"
        if choice == aux_offset + 1:
            return "exit"

        print("Choice out of range. Try again.")
