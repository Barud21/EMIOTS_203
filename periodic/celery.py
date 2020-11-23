from celery import Celery
from celery.schedules import crontab

app = Celery('periodic',
             include=['periodic.tasks'])

app.config_from_object('periodic.celeryconfig')

# this is a default configuration for scheduling periodic tasks
# actual config is stored in the database through django-celery-beat
app.conf.beat_schedule = {
 'testTask': {
    'task': 'periodic.tasks.check',
    'schedule': crontab(minute='*/10')
    },
 'realTask': {
    'task': 'periodic.tasks.createOrUpdateTweetsDataFile',
    'schedule': crontab(hour=21, minute=30)
    }
}
