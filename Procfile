web: gunicorn project.wsgi --log-file -
worker: celery -A periodic worker --pool=solo --loglevel=info --heartbeat-interval=600
beat: celery -A periodic beat --loglevel=info
