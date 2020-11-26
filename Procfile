release: python manage.py migrate --noinput
web: gunicorn project.wsgi --log-file -
worker_and_beat: celery -A periodic worker --pool=solo --loglevel=info --heartbeat-interval=600 --beat
