#!/usr/bin/env python3
"""Run backend and frontend dev servers in one command."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = ROOT / "server"
CLIENT_DIR = ROOT / "client"
VENV_DIR = SERVER_DIR / "venv"


def fail(message: str, exit_code: int = 1) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(exit_code)


def venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def launch_processes() -> tuple[subprocess.Popen, subprocess.Popen]:
    backend_python = venv_python()
    if not backend_python.exists():
        fail(
            "Backend virtual environment not found. "
            "Run 'python scripts/build_env.py' first."
        )

    print("Starting backend on http://127.0.0.1:8000 ...")
    backend = subprocess.Popen(
        [str(backend_python), "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=SERVER_DIR,
    )

    print("Starting frontend on http://127.0.0.1:5173 ...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
        cwd=CLIENT_DIR,
    )

    return backend, frontend


def terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return

    if os.name == "nt":
        proc.terminate()
    else:
        proc.send_signal(signal.SIGTERM)


def main() -> None:
    backend, frontend = launch_processes()

    print("Both dev servers are running. Press Ctrl+C to stop both.")

    try:
        while True:
            backend_rc = backend.poll()
            frontend_rc = frontend.poll()

            if backend_rc is not None:
                print(f"Backend exited with code {backend_rc}. Stopping frontend.")
                terminate_process(frontend)
                raise SystemExit(backend_rc)

            if frontend_rc is not None:
                print(f"Frontend exited with code {frontend_rc}. Stopping backend.")
                terminate_process(backend)
                raise SystemExit(frontend_rc)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping both servers...")
        terminate_process(frontend)
        terminate_process(backend)

        try:
            frontend.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend.kill()

        try:
            backend.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend.kill()

        print("Stopped.")


if __name__ == "__main__":
    main()
