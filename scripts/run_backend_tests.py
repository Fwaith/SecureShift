#!/usr/bin/env python3
"""Run Django tests for selected SecureShift backend apps."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
VENV_DIR = SERVER_DIR / "venv"

# Keep the default scope narrow to the project's core apps.
DEFAULT_TEST_LABELS = ["accounts", "reports", "habitability"]


def fail(message: str, exit_code: int = 1) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(exit_code)


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


def run_tests(py: str, test_labels: list[str]) -> None:
    if not (SERVER_DIR / "manage.py").exists():
        fail("manage.py was not found in server directory.")

    cmd = [py, "manage.py", "test", *test_labels]
    printable = " ".join(cmd)
    print(f"\n> {printable}")

    subprocess.run(cmd, cwd=str(SERVER_DIR), check=True)



def main() -> None:
    print("=== SecureShift backend tests ===")
    py = resolve_python()
    run_tests(py, DEFAULT_TEST_LABELS)
    print("\nBackend test run complete.")


if __name__ == "__main__":
    main()
