from django.core import mail
from django.test import TestCase
from django.utils import timezone
from tasks.models import Task
from users.models import User
from tasks.tasks import send_task_notification_email, send_status_change_email, send_task_reminders
from datetime import timedelta, datetime
from unittest.mock import patch


class EmailTaskTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test',
            password='123456',
            email='trinhxuanphuong39@gmail.com',
            role='admin'
        )
        self.staff = User.objects.create_user(
            username='staff_test',
            password='password',
            email='himinngaming@gmail.com',
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
            'due_date': timezone.now() + timedelta(hours=24),
        }
        defaults.update(kwargs)
        return Task.objects.create(**defaults)

    def test_send_task_notification_email(self):
        task = self.create_task()
        send_task_notification_email(task.id)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn(task.title, mail.outbox[0].subject)

    def test_send_status_change_email(self):
        task = self.create_task()
        task.status = 'completed'
        task.save()
        send_status_change_email(task.id)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn("đã được", mail.outbox[-1].subject.lower())

    @patch('django.utils.timezone.now')
    def test_send_deadline_reminder_email(self, mock_now):
        # Giả lập hệ thống đang ở 8:00 sáng
        fake_now = timezone.make_aware(datetime(2025, 7, 8, 8, 0, 0))
        mock_now.return_value = fake_now

        # Task đến hạn trong vòng 24h -> sẽ được gửi nhắc
        task = self.create_task(due_date=fake_now + timedelta(hours=5))
        send_task_reminders()

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn('nhắc việc', mail.outbox[-1].subject.lower())

