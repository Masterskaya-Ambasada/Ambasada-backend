import multiprocessing
import os

bind = '0.0.0.0:8000'

# если используется несколько workers - Telebot
# работает нестабильно. Для небольшой нагрузки это нормально.
workers = multiprocessing.cpu_count() * 2 + 1

max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 2000))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', 400))

accesslog = '-'
chdir = '/code/backend'
worker_tmp_dir = '/dev/shm'  # noqa: S108
