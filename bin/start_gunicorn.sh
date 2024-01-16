source /home/mamba/PycharmProjects/ktep-study-load/venv/bin/activate
exec gunicorn -c "/home/mamba/PycharmProjects/ktep-study-load/study_load/gunicorn_config.py" study_load.wsgi