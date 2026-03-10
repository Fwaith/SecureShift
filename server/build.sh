#!/bin/bash

# SecureShift - Complete Build Script
# Exit on any error
set -e

echo "======================================"
echo "🚀 SECURESHIFT BACKEND BUILD STARTING"
echo "======================================"

# Print Python version for debugging
echo "🐍 Python version:"
python --version

# Install dependencies
echo "📦 Installing Python packages from requirements.txt..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Create cache tables (if using database cache)
echo "⚙️ Creating cache tables..."
python manage.py createcachetable || true

# Collect static files
echo "🖼️ Collecting static files..."
python manage.py collectstatic --noinput

# Create default superuser (for development/demo)
echo "👤 Setting up default superuser (admin)..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✓ Superuser "admin" created')
else:
    print('✓ Superuser already exists')
END

# Load initial fixtures (sample data)
echo "📊 Loading initial data from fixtures..."

# Habitability app fixtures
echo "  - Loading habitability areas..."
python manage.py loaddata areas.json || echo "  ⚠️ No areas.json fixture found"

echo "  - Loading report categories..."
python manage.py loaddata categories.json || echo "  ⚠️ No categories.json fixture found"

# Reports app fixtures
echo "  - Loading sample reports..."
python manage.py loaddata sample_reports.json || echo "  ⚠️ No sample_reports.json fixture found"

# Check if everything worked
echo "✅ Verifying database setup..."
python manage.py check

echo "======================================"
echo "✅ SECURESHIFT BACKEND BUILD COMPLETE"
echo "======================================"
