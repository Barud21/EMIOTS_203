from periodic.celery import app


@app.task
def check():
    print('I am a test task!')
