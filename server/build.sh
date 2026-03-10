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
python manage.py migrate --noinput
echo "✅ Migrations complete"
echo ""

# Collect static files
echo "🖼️ Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"
echo ""

# Create default superuser for development/demo (if it doesn't exist)
echo "👤 Setting up default superuser..."
python manage.py shell << 'END'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✓ Superuser "admin" created with password "admin123"')
else:
    print('✓ Superuser already exists')
END
echo ""

# Load fixtures (sample data) - but don't fail if they don't exist
echo "📊 Loading initial data from fixtures..."

# Habitability app fixtures
echo "  - Loading habitability areas..."
python manage.py loaddata areas.json 2>/dev/null || echo "  ⚠️ No areas.json fixture found"

echo "  - Loading report categories..."
python manage.py loaddata categories.json 2>/dev/null || echo "  ⚠️ No categories.json fixture found"

# Reports app fixtures
echo "  - Loading sample reports..."
python manage.py loaddata sample_reports.json 2>/dev/null || echo "  ⚠️ No sample_reports.json fixture found"

echo "✅ Fixture loading complete"
echo ""

# Verify everything is working
echo "🔍 Running system check..."
python manage.py check
echo "✅ System check passed"
echo ""

echo "========================================="
echo "✅ SECURESHIFT BACKEND BUILD COMPLETE"
echo "========================================="
echo "🌐 Live at: https://secureshift-aqof.onrender.com"
echo "📅 Build finished: $(date)"
