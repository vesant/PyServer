# PyServer Manager

PyServer Manager is an interactive Python CLI that lets you start and stop the services that live in this repository without leaving a single terminal window. It reads a YAML configuration that lists your lab apps and their commands (for example `npm run start:linux`) and runs them in-place, streaming the output directly inside the manager.

## Features

- Menu-driven interface with reload and exit controls
- Streams command output without spawning extra terminals
- Gracefully interrupts long-running processes with `Ctrl+C`
- Environment variable overrides per app entry
- YAML configuration that lives alongside your project

## Project layout

```
.
├── config/
│   └── apps.yaml           # Example managed apps configuration
├── src/
│   └── pyserver_manager/
│       ├── __init__.py
│       ├── app.py          # Entry point (`python -m pyserver_manager.app`)
│       ├── config.py       # YAML loader and validation
│       ├── menu.py         # Text menu renderer
│       └── runner.py       # Command execution helpers
├── tests/
│   └── test_config.py      # Unit tests for config loading
├── README.md
└── requirements.txt
```

## Getting started

1. Create a virtual environment (recommended) and install dependencies:

   **PowerShell**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

   **Linux/macOS shell**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Adjust `config/apps.yaml` to match your services. Each entry supports:

   - `name`: Display name in the menu.
   - `command`: Shell command executed for the app.
   - `cwd`: Working directory relative to `config/apps.yaml`.
   - `description` *(optional)*: Extra info shown in the menu.
   - `env` *(optional)*: Environment variable overrides.


## Reloading configuration

Choose **Reload configuration** in the menu to re-read `apps.yaml` after making changes. If the new config has an error, the previous one stays active.

## Custom config path

You can point to another configuration file:

```powershell
python -m pyserver_manager.app --config /path/to/another/apps.yaml
```

## Requirements

- Python 3.11+
- Works best on Unix-like shells (commands such as `npm run start:linux` rely on your environment).

## Next steps

- Add additional management commands (e.g., status checks, logs)
- Integrate health probes or service discovery if your lab grows

## Launcher script

A small cross-platform launcher `run.py` is included at the project root. It simplifies running the manager by selecting the repository virtual environment (if present) and invoking the package entry point.

Features:
- Auto-detects common venv folders in the repo root: `.venv`, `venv`, `env`.
- Picks the correct Python executable for the platform (Windows uses `Scripts\python.exe`, Unix uses `bin/python`).
- Falls back to the current interpreter if no virtualenv is found.
- Supports `--dry-run` (prints the chosen python and command without running) and `--config` to forward a custom `apps.yaml` path.

Examples (PowerShell):

```powershell
# Dry-run to see the selected python and command
python run.py --dry-run

# Start the manager (run.py will pick the repo venv if available)
python run.py

# Start with a custom config file
python run.py --config D:\path\to\apps.yaml

# Forward extra args to the manager after `--`
python run.py -- --some-manager-flag value
```

The launcher is optional — you can still run the manager directly with `python -m pyserver_manager.app` or install the package (`pip install -e .`) so the package is importable in your environment.
