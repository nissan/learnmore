#!/bin/bash

# Activate virtual environment
source /var/www/djangoapps/learnmore/venv/bin/activate

# Set environment variables (add any other environment variables you need)
export DJANGO_SETTINGS_MODULE=learnmore.settings
export PYTHONPATH=/home/s4512158/www/djangoapps/learnmore

# Start Gunicorn with the configuration file
cd /home/s4512158/www/djangoapps/learnmore
exec gunicorn -c gunicorn_config.py learnmore.wsgi:application 