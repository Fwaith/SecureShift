#!/usr/bin/env python3
"""Reset local SQLite database and repopulate required seed data."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
VENV_DIR = SERVER_DIR / "venv"
DB_PATH = SERVER_DIR / "db.sqlite3"


def fail(message: str, exit_code: int = 1) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(exit_code)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    printable = " ".join(cmd)
    print(f"\n> {printable}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def resolve_python() -> str:
    candidate = venv_python()
    if candidate.exists():
        return str(candidate)

    print("Virtual environment not found. Falling back to current Python interpreter.")
    return sys.executable


def reset_database() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Deleted {DB_PATH}")
    else:
        print(f"No database file found at {DB_PATH}; continuing.")


def rebuild_schema_and_data(py: str) -> None:
    if not (SERVER_DIR / "manage.py").exists():
        fail("manage.py was not found in server directory.")

    commands = [
        [py, "manage.py", "makemigrations"],
        [py, "manage.py", "migrate"],
        [py, "manage.py", "import_habitability_data", "./HabitabilityData.csv"],
        [py, "manage.py", "create_admin_account"],
        [py, "manage.py", "import_outcode_mappings"],
    ]

    for cmd in commands:
        run(cmd, cwd=SERVER_DIR)


def main() -> None:
    print("=== SecureShift database reset ===")
    py = resolve_python()
    reset_database()
    rebuild_schema_and_data(py)
    print("\nDatabase reset complete.")


if __name__ == "__main__":
    main()
