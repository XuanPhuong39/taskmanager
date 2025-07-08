import pytest
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from tasks.models import Task
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def get_token(api_client):
    def _get_token(user):
        password = "123456" if user.role == "admin" else ("123456abc#" if user.role == "manager" else "password")
        response = api_client.post("/api/token/", {"username": user.username, "password": password})
        return response.data["access"]
    return _get_token

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username='admin_test', email='admin@example.com', password='123456', role='admin', is_staff=True)

@pytest.fixture
def manager_user(db):
    return User.objects.create_user(username='manager_test', email='manager@example.com', password='123456abc#', role='manager')

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='staff_test', email='staff@example.com', password='password', role='staff')


class TaskEdgeCasesTests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staffuser', password='password', role='staff')
        self.token = str(RefreshToken.for_user(self.staff).access_token)

    def test_staff_cannot_assign_task_to_others(self):
        other_user = User.objects.create_user(username='other', password='password', role='staff')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        payload = {
            'title': 'Invalid Assign',
            'description': 'Staff tries to assign to other',
            'status': 'pending',
            'priority': 'low',
            'owner': self.staff.id,
            'assignee': other_user.id
        }

        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Staff chỉ có thể gán task cho chính mình.')


    def test_unauthorized_user_cannot_access(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

@pytest.mark.django_db
def test_create_task_missing_title(api_client, admin_user, staff_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    data = {
        # "title": "Thiếu title",
        "description": "Không có tiêu đề",
        "status": "pending",
        "priority": "medium",
        "owner": admin_user.id,
        "assignee": staff_user.id
    }
    response = api_client.post("/api/tasks/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'title' in response.data

@pytest.mark.django_db
def test_create_task_missing_assignee(api_client, admin_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    data = {
        "title": "Thiếu assignee",
        "description": "Không ai nhận",
        "status": "pending",
        "priority": "high",
        "owner": admin_user.id
    }
    response = api_client.post("/api/tasks/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'assignee' in response.data

@pytest.mark.django_db
def test_create_task_missing_owner(api_client, admin_user, staff_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    data = {
        "title": "Không có owner",
        "description": "Thiếu người giao",
        "status": "pending",
        "priority": "medium",
        "assignee": staff_user.id
        # thiếu 'owner'
    }
    response = api_client.post("/api/tasks/", data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'owner' in response.data

@pytest.mark.django_db
def test_create_task_invalid_status(api_client, admin_user, staff_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    data = {
        "title": "Sai status",
        "description": "Test",
        "status": "invalid_status",  # sai
        "priority": "low",
        "owner": admin_user.id,
        "assignee": staff_user.id
    }
    response = api_client.post("/api/tasks/", data)
    assert response.status_code == 400
    assert 'status' in response.data

@pytest.mark.django_db
def test_update_task_with_invalid_id(api_client, admin_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.patch('/api/tasks/9999/', {"status": "completed"})
    assert response.status_code == 404

@pytest.mark.django_db
def test_create_task_with_nonexistent_assignee(api_client, admin_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Invalid assignee",
        "description": "Người nhận không tồn tại",
        "status": "pending",
        "priority": "medium",
        "owner": admin_user.id,
        "assignee": 9999  # ID không tồn tại
    }

    response = api_client.post("/api/tasks/", data)
    assert response.status_code == 400
    assert 'assignee' in response.data

@pytest.mark.django_db
def test_create_task_with_nonexistent_owner(api_client, staff_user, get_token):
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    data = {
        "title": "Invalid owner",
        "description": "Người giao không tồn tại",
        "status": "pending",
        "priority": "medium",
        "owner": 9999,  # Không tồn tại
        "assignee": staff_user.id
    }

    response = api_client.post("/api/tasks/", data)
    assert response.status_code == 400
    assert 'owner' in response.data

@pytest.mark.django_db
def test_delete_nonexistent_task(api_client, admin_user, get_token):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = api_client.delete('/api/tasks/123456/')
    assert response.status_code == 404
import pytest
from rest_framework import status

@pytest.mark.django_db
def test_stats_forbidden_for_staff(api_client, staff_user, get_token):
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = api_client.get('/api/stats/')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'detail' in response.data
