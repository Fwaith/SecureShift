#!/bin/bash

# SecureShift - Production Build Script
# Exit immediately if any command fails
set -e

echo "========================================="
echo "🚀 SECURESHIFT BACKEND BUILD STARTING"
echo "========================================="
echo "📅 Build time: $(date)"
echo ""

# Print Python version for debugging
echo "🐍 Python version:"
python --version
echo ""

# Install dependencies
echo "📦 Installing Python packages from requirements.txt..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
echo "✅ Migrations complete"
echo ""

# Create default superuser for development/demo (if it doesn't exist)
echo "👤 Adding admin account..."
python manage.py create_admin_account
echo ""

# Habitability app fixtures
echo "  - Loading habitability scores..."
python manage.py import_habitability_data ./HabitabilityData.csv
echo ""

echo "  - Loading outcode -> county mappings..."
python manage.py import_outcode_mappings
echo "✅ Loaded external data"
echo ""

# Verify everything is working
echo "🔍 Running system check..."
python manage.py check
echo "✅ System check passed"
echo ""

echo "========================================="
echo "✅ SECURESHIFT BACKEND BUILD COMPLETE"
echo "========================================="
echo "Run with command 'python manage.py runserver' to start the backend server."
