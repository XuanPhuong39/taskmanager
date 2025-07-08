from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from tasks.models import Task
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class TaskStatsTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager_test', password='123456abc#', role='manager')
        self.token = str(RefreshToken.for_user(self.manager).access_token)

        Task.objects.create(title='Task 1', status='pending', priority='low', owner=self.manager, assignee=self.manager)
        Task.objects.create(title='Task 2', status='completed', priority='high', owner=self.manager, assignee=self.manager)

    def test_get_task_stats(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pending', response.data)
        self.assertIn('completed', response.data)
