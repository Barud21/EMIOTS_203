from celery import Celery
from celery.schedules import crontab

app = Celery('periodic',
             include=['periodic.tasks'])

app.config_from_object('periodic.celeryconfig')

app.conf.beat_schedule = {
 'runme': {
    'task': 'periodic.tasks.check',
    'schedule': crontab(minute='*/2')
    }
}
