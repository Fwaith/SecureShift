#!/usr/bin/env python3
"""Build backend and frontend environments in a cross-platform way."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
CLIENT_DIR = ROOT / "client"
VENV_DIR = SERVER_DIR / "venv"
PYTHON_MIN = (3, 12)


def fail(message: str, exit_code: int = 1) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(exit_code)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    printable = " ".join(cmd)
    print(f"\n> {printable}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def find_cmd(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        fail(f"'{cmd}' is required but was not found in PATH.")
    return path


def get_venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_python() -> None:
    if sys.version_info < PYTHON_MIN:
        fail(
            "Python 3.12+ is required. "
            f"Detected {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}."
        )
    print(
        "Python version OK: "
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )


def ensure_node_tooling() -> None:
    node = find_cmd("node")
    npm = find_cmd("npm")

    node_version = subprocess.check_output([node, "--version"], text=True).strip()
    npm_version = subprocess.check_output([npm, "--version"], text=True).strip()

    print(f"Node detected: {node_version}")
    print(f"npm detected: {npm_version}")


def ensure_venv() -> Path:
    if not VENV_DIR.exists():
        print(f"Creating virtual environment at {VENV_DIR}...")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        print(f"Virtual environment already exists at {VENV_DIR}.")

    venv_python = get_venv_python()
    if not venv_python.exists():
        fail(f"Could not find venv Python executable at: {venv_python}")

    return venv_python


def install_backend_requirements(venv_python: Path) -> None:
    requirements = SERVER_DIR / "requirements.txt"
    if not requirements.exists():
        fail(f"Backend requirements file not found at: {requirements}")

    run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=SERVER_DIR)
    run([str(venv_python), "-m", "pip", "install", "-r", str(requirements)], cwd=SERVER_DIR)


def install_frontend_requirements() -> None:
    lockfile = CLIENT_DIR / "package-lock.json"
    npm = find_cmd("npm")

    if lockfile.exists():
        run([npm, "ci"], cwd=CLIENT_DIR)
    else:
        run([npm, "install"], cwd=CLIENT_DIR)


def bootstrap_backend_data(venv_python: Path) -> None:
    manage_py = SERVER_DIR / "manage.py"
    if not manage_py.exists():
        fail(f"manage.py not found at: {manage_py}")

    commands = [
        [str(venv_python), "manage.py", "makemigrations"],
        [str(venv_python), "manage.py", "migrate"],
        [str(venv_python), "manage.py", "import_habitability_data", "./HabitabilityData.csv"],
        [str(venv_python), "manage.py", "create_admin_account"],
        [str(venv_python), "manage.py", "import_outcode_mappings"],
    ]

    for cmd in commands:
        run(cmd, cwd=SERVER_DIR)


def main() -> None:
    print("=== SecureShift environment build ===")
    ensure_python()
    ensure_node_tooling()
    venv_python = ensure_venv()

    print("\nInstalling backend dependencies...")
    install_backend_requirements(venv_python)

    print("\nInstalling frontend dependencies...")
    install_frontend_requirements()

    print("\nBootstrapping backend database and seed data...")
    bootstrap_backend_data(venv_python)

    print("\nSetup complete.")
    print("Run: python scripts/run_dev.py")


if __name__ == "__main__":
    main()
