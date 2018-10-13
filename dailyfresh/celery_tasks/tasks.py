
from celery import Celery
from django.core.mail import send_mail


app = Celery('celery_tasks.tasks', broker='redis://localhost/2')


import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()

@app.task
def task_send_mail(subject, message,sender,receiver,html_message):
    print('start...')
    import time
    time.sleep(10)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    print('end...')