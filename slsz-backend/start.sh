#!/bin/bash
# Prepare for django
python manage.py makemigrations
python manage.py migrate
# python manage.py createplatformadmin
# Start uwsgi
uwsgi --ini uwsgi.ini
