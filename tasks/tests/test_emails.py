from django.core import mail
from django.test import TestCase
from django.utils import timezone
from tasks.models import Task
from users.models import User
from tasks.tasks import (
    send_task_notification_email,
    send_status_change_email,
    send_task_reminders,
)
from datetime import timedelta, datetime
from unittest.mock import patch


class EmailTaskTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            password='123456',
            email='himinngaming@gmail.com',
            role='admin'
        )
        self.staff = User.objects.create_user(
            username='staff_test',
            password='password',
            email='trinhxuanphuong39@gmail.com',
            role='staff'
        )

    def create_task(self, **kwargs):
        defaults = {
            'title': 'Email Test Task',
            'description': 'Should trigger email',
            'status': 'pending',
            'priority': 'medium',
            'owner': self.admin,
            'assignee': self.staff,
            'due_date': timezone.now() + timedelta(hours=22),
        }
        defaults.update(kwargs)

        # Đảm bảo due_date là timezone-aware
        if 'due_date' in defaults and timezone.is_naive(defaults['due_date']):
            defaults['due_date'] = timezone.make_aware(defaults['due_date'])

        return Task.objects.create(**defaults)


    def test_send_task_notification_email(self):
        task = self.create_task()
        send_task_notification_email(task.id)

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn(task.title.lower(), mail.outbox[0].subject.lower())

    def test_send_status_change_email(self):
        task = self.create_task()
        task.status = 'completed'
        task.save()
        send_status_change_email(task.id)

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("đã được", mail.outbox[-1].subject.lower())

    @patch('django.utils.timezone.now')
    def test_send_deadline_reminder_email(self, mock_now):
        # Giả lập thời gian là 2025-07-09 08:00:00
        fake_now = timezone.make_aware(datetime(2025, 7, 9, 8, 0, 0))
        mock_now.return_value = fake_now

        # Task đến hạn trong vòng 24h (ví dụ: 07:59 sáng 10/7)
        due = fake_now + timedelta(hours=23, minutes=59)
        task = self.create_task(due_date=due)

        # Đảm bảo created_at nằm trong khoảng valid (optional)
        task.created_at = fake_now
        task.save(update_fields=["created_at"])

        send_task_reminders()

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("nhắc việc", mail.outbox[-1].subject.lower())
