from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-task-reminders-every-morning': {
        'task': 'tasks.tasks.send_task_reminders',
        'schedule': crontab(hour=8, minute=0),  # chạy lúc 8:00 sáng mỗi ngày
    },
}
