# SecureShift

SecureShift is a full-stack project with:
- Django backend in `server/`
- Vue (Vite) frontend in `client/`

## Quick Start (Local)

Run these commands from the repo root:

1. Build both environments (backend + frontend):
	 python scripts/build_env.py

2. Start both backend and frontend dev sessions:
	 python scripts/run_dev.py

The app should be available at:
- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000

## Notes

- A default admin account is created during setup/reset:
	- Email: `admin@secureshift.com`
	- Password: `test1234`
- Additional accounts can be registered normally, but they start without admin permissions.
- If backend install fails on `psycopg2-binary`, switch to `psycopg2` in `server/requirements.txt` and rerun `python scripts/build_env.py`.
- If you change models, rerun `python scripts/reset_database.py` for a clean local state.

## Scripts

### 1) Build environments
Command:
python scripts/build_env.py

What it does:
- Validates required tooling (Python, Node, npm)
- Creates `server/venv` if needed
- Installs backend dependencies from `server/requirements.txt`
- Installs frontend dependencies from `client/package-lock.json` / `client/package.json`
- Runs backend migrations and data setup commands:
	- `python manage.py makemigrations`
	- `python manage.py migrate`
	- `python manage.py import_habitability_data ./HabitabilityData.csv`
	- `python manage.py create_admin_account`
	- `python manage.py import_outcode_mappings`

### 2) Reset database
Command:
python scripts/reset_database.py

What it does:
- Deletes `server/db.sqlite3`
- Rebuilds DB state by running:
	- `python manage.py makemigrations`
	- `python manage.py migrate`
	- `python manage.py import_habitability_data ./HabitabilityData.csv`
	- `python manage.py create_admin_account`
	- `python manage.py import_outcode_mappings`

### 3) Run frontend + backend
Command:
python scripts/run_dev.py

What it does:
- Starts Django in `server/`
- Starts Vite in `client/`
- Streams both logs to one terminal
- Stops both processes on Ctrl+C