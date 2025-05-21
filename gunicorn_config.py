import multiprocessing

# Gunicorn configuration for LearnMore application

# Bind to specific IP and port
bind = "0.0.0.0:8000"

# Workers - recommended formula is (2 * cpu_count + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class - choose one that fits your needs
worker_class = "sync"  # Options: sync, eventlet, gevent, tornado, gthread

# Maximum requests before worker restart (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Timeout (in seconds)
timeout = 30

# Keep the process alive
daemon = False

# Log configuration
accesslog = "/var/www/djangoapps/learnmore/logs/access.log"
errorlog = "/var/www/djangoapps/learnmore/logs/error.log"
loglevel = "info"

# Process naming
proc_name = "learnmore_gunicorn"

# Set Django's settings module
raw_env = ["DJANGO_SETTINGS_MODULE=learnmore.settings"]

# Change to project directory
chdir = "/home/s4512158/www/djangoapps/learnmore/learnmore" 