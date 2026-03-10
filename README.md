# SecureShift

## Instructions
- Clone the git repo
- In Render go to Blueprints → new blueprint instance
- connect to repo
- render.yaml acts as the blueprint

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
