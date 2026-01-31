#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create admin user if it doesn't exist (try both methods)
echo "Creating admin user..."
python manage.py ensure_admin || python create_admin_on_deploy.py
echo "Admin user setup complete"
