command = '/home/mamba/PycharmProjects/ktep-study-load/venv/bin/gunicorn'
pythonpath = '/home/mamba/PycharmProjects/ktep-study-load/study_load'
bind = '127.0.0.1:8000'
workers = 5
user = 'mamba'
limit_request_fields = 32000
limit_request_fields_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=study_load.settings'