echo "If you encounter issues installing psycopg2, try switching between 'psycopg2', and 'psycopg2-binary' in requirements.txt and run this setup script again."
read -p "Acknowledged (enter)"

# Create a VENV in server folder
cd server

# Find what the python command is
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Python is not installed. Please install Python 3.6 or higher."
    exit 1
fi

# Ensure venv module is available
if ! $PYTHON_CMD -m venv --help &>/dev/null; then
    echo "The venv module is not available. Please ensure you have Python 3.6 or higher installed."
    exit 1
fi

# Create the virtual environment
$PYTHON_CMD -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup DB (run makemigrations, migrate, import_habitability_data ./HabitabilityData.csv, create_admin_account)
python manage.py makemigrations
python manage.py migrate
python manage.py import_habitability_data ./HabitabilityData.csv
python manage.py create_admin_account


cd ../client

# Ensure npm is installed
if ! command -v npm &>/dev/null; then
    echo "npm is not installed. Please install Node.js and npm."
    exit 1
fi

# Install dependencies
npm install

echo ""
echo "*****************************"
echo "Setup completed successfully!"
echo "*****************************"
echo ""

echo "To run the server, activate the virtual environment with 'source server/venv/bin/activate' and then run 'python server/manage.py runserver'."
echo ""

echo "To run the client, open another terminal and run 'cd client && npm run dev'."

cd ..