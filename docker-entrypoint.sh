#!/bin/bash
set -e

# Create database directory if it doesn't exist
mkdir -p /app/instance

# Initialize the database
echo "Initializing database..."
python -c "from app import app; from models import User, RoleEnum; from __init__ import db; app.app_context().push(); db.create_all(); admin = User.query.filter_by(role=RoleEnum.ADMIN).first(); print('Admin user already exists.' if admin else 'No admin user found, creating default one...'); exit(0);"

# Check if environment variables are set
if [ -z "$PUSHBULLET_KEY" ] || [ -z "$EMAIL_MESSAGERIE" ] || [ -z "$EMAIL_MESSAGERIE_PASSWORD" ]; then
    echo "Warning: One or more required environment variables are not set."
    echo "PUSHBULLET_KEY: ${PUSHBULLET_KEY:-(not set)}"
    echo "EMAIL_MESSAGERIE: ${EMAIL_MESSAGERIE:-(not set)}"
    echo "EMAIL_MESSAGERIE_PASSWORD: ${EMAIL_MESSAGERIE_PASSWORD:-(not set)}"
fi

echo "Starting application..."
exec "$@"
