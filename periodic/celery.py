from celery import Celery
from celery.schedules import crontab

app = Celery('periodic',
             include=['periodic.tasks'])

app.config_from_object('periodic.celeryconfig')

app.conf.beat_schedule = {
 'testTask': {
    'task': 'periodic.tasks.check',
    'schedule': crontab(minute='*/5')
    },
 'realTask': {
    'task': 'periodic.tasks.createOrUpdateTweetsDataFile',
    'schedule': crontab(hour=21, minute=30)
    }
}
