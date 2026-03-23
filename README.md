# SecureShift

## Instructions
- Clone the git repo
- In Render go to Blueprints → new blueprint instance
- connect to repo
- render.yaml acts as the blueprint

## To-do
[Issue board](https://git.cs.bham.ac.uk/software-engineering-2025-26/AlgorithmAlliance/-/boards)

## Note

**build.sh:**
- Installs dependencies
- Runs migrations
- Collects static files
- Loads fixtures

Database tables and relationships can be made using Models which are located inside models.py in each app folder

Data can be hardcoded using fixtures in the fixtures dir in each app (not made yet)

**Render doesn't show the tables so maybe use:**
- Render Shell: python manage.py dbshell
- PSQL client

**When changing models:**
1. python manage.py makemigrations
2. python manage.py migrate
3. run `python manage.py import_habitability_data ./HabitabilityData.csv` from inside the `server` dir
3. run `python manage.py create_admin_account` from inside the `server` dir