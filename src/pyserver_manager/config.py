from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

import yaml


@dataclass(slots=True)
class AppDefinition:
    """Represents a single managed application entry."""

    name: str
    command: str
    working_dir: Path
    description: str | None = None
    environment: Dict[str, str] = field(default_factory=dict)

    def resolved_working_dir(self, root: Path) -> Path:
        """Return the absolute working directory for the app."""
        candidate = (root / self.working_dir).resolve()
        if not candidate.exists():
            raise FileNotFoundError(
                f"Working directory '{candidate}' for app '{self.name}' does not exist."
            )
        return candidate


@dataclass(slots=True)
class ManagerConfig:
    apps: List[AppDefinition]

    @classmethod
    def from_mapping(cls, mapping: Dict[str, object], base_dir: Path) -> "ManagerConfig":
        raw_apps = mapping.get("apps")
        if not raw_apps:
            raise ValueError("Configuration file must define at least one app under 'apps'.")
        apps: List[AppDefinition] = []
        for raw in _ensure_iterable(raw_apps):
            app = _parse_app(raw, base_dir)
            apps.append(app)
        return cls(apps=apps)


def load_config(path: Path) -> ManagerConfig:
    """Load the manager configuration from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    base_dir = path.parent
    return ManagerConfig.from_mapping(data, base_dir)


def _parse_app(raw: Dict[str, object], base_dir: Path) -> AppDefinition:
    if not isinstance(raw, dict):
        raise TypeError("App definition must be a mapping.")

    name = raw.get("name")
    command = raw.get("command")
    working_dir = raw.get("cwd") or raw.get("path") or "."
    description = raw.get("description")
    environment = raw.get("env") or {}

    if not name or not command:
        raise ValueError("Each app must include both 'name' and 'command'.")

    app = AppDefinition(
        name=str(name),
        command=str(command),
        working_dir=Path(str(working_dir)),
        description=str(description) if description else None,
        environment={str(k): str(v) for k, v in environment.items()},
    )
    # Validate the working directory eagerly to help catch mistakes early.
    app.resolved_working_dir(base_dir)
    return app


def _ensure_iterable(value: object) -> Iterable[Dict[str, object]]:
    if isinstance(value, list):
        return value
    return [value]  # type: ignore[return-value]
