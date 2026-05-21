import multiprocessing
import os

bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

# if more than one worker - Telebot
# works unstable. It's ok for small load.
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))

max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 2000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 400))

accesslog = '-'
chdir = '/code/backend'
worker_tmp_dir = '/dev/shm'  # noqa: S108
