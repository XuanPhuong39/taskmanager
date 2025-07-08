# tasks/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from .models import Task
from django.conf import settings

@shared_task
def send_task_notification_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        subject = f"Công việc được tạo: {task.title}"
        message = f"Công việc '{task.title}' đã được tạo với trạng thái {task.status}."
        recipients = [task.owner.email]

        if task.assignee and task.assignee.email:
            recipients.append(task.assignee.email)

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipients,
            fail_silently=False,
        )
    except Exception as e:
        print("Error sending task notification:", e)

@shared_task
def send_task_reminders():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    tasks = Task.objects.filter(
        due_date__gte=today,
        due_date__lte=tomorrow,
        status__in=['pending', 'in_progress']
    )
    for task in tasks:
        if task.assignee and task.assignee.email:
            send_mail(
                subject=f"Nhắc việc: {task.title}",
                message=f"Bạn có một công việc sắp đến hạn vào {task.due_date}",
                from_email="no-reply@example.com",
                recipient_list=[task.assignee.email],
            )

@shared_task
def send_status_change_email(task_id):
    try:
        task = Task.objects.get(id=task_id)
        if task.assignee and task.assignee.email:
            recipient = task.assignee.email
        else:
            recipient = settings.DEFAULT_FROM_EMAIL  # fallback
        
        send_mail(
            subject=f"[Cập nhập công việc] '{task.title}' đã được {task.status}",
            message=f"Trạng thái của công việc '{task.title}' đã được thay đổi thành '{task.status}'.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Task.DoesNotExist:
        pass
