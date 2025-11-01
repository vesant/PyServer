from pathlib import Path

import pytest

from pyserver_manager.config import AppDefinition, ManagerConfig, load_config


def _write_config(path: Path, payload: str) -> Path:
    path.write_text(payload, encoding="utf-8")
    return path


def test_load_config_success(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    target_dir = config_dir / "apps" / "dashboard"
    target_dir.mkdir(parents=True)

    config_file = _write_config(
        config_dir / "apps.yaml",
        """
apps:
  - name: dashboard
    command: npm run start:linux
    cwd: apps/dashboard
    description: Demo dashboard
    env:
      NODE_ENV: development
        """.strip(),
    )

    config = load_config(config_file)

    assert isinstance(config, ManagerConfig)
    assert len(config.apps) == 1
    app = config.apps[0]
    assert isinstance(app, AppDefinition)
    assert app.name == "dashboard"
    assert app.command == "npm run start:linux"
    assert app.description == "Demo dashboard"
    assert app.environment == {"NODE_ENV": "development"}
    assert app.resolved_working_dir(config_dir) == target_dir


def test_load_config_requires_apps_key(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = _write_config(config_dir / "apps.yaml", "{}")

    with pytest.raises(ValueError):
        load_config(config_file)


def test_load_config_validates_working_directory(tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = _write_config(
        config_dir / "apps.yaml",
        """
apps:
  - name: missing
    command: echo missing
    cwd: apps/missing
        """.strip(),
    )

    with pytest.raises(FileNotFoundError):
        load_config(config_file)
