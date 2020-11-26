import os

broker_url = os.getenv('RabbitMqUrl')
timezone = 'Europe/Warsaw'

beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
