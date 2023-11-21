#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

echo "Create superuser"
python manage.py createsuperuser --noinput 

echo "Starting server"
python manage.py runserver 0.0.0.0:8000