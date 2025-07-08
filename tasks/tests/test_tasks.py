import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tasks.models import Task
from users.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return User.objects.create_user(username='admin_test', email='trinhxuanphuong39@gmail.com', password='123456', role='admin', is_staff=True)

@pytest.fixture
def manager_user(db):
    return User.objects.create_user(username='manager_test', email='txphuonggg@gmail.com', password='123456abc#', role='manager')

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='staff_test', email='himinngaming@gmail.com', password='password', role='staff')

@pytest.fixture
def create_tasks(admin_user, staff_user):
    return [
        Task.objects.create(title=f'Task {i}', description='desc', owner=admin_user, assignee=staff_user)
        for i in range(3, 22)
    ]

@pytest.fixture
def get_token(api_client):
    def _get_token(user):
        response = api_client.post('/api/token/', {'username': user.username, 'password': '123456' if user.role == 'admin' else ('123456abc#' if user.role == 'manager' else 'password')})
        return response.data['access']
    return _get_token

def test_admin_can_view_all_tasks(api_client, admin_user, get_token, create_tasks):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get('/api/tasks/')
    assert response.status_code == 200
    assert len(response.data) == len(create_tasks)

def test_staff_only_sees_tasks_assigned_to_them(api_client, staff_user, get_token, create_tasks):
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get('/api/tasks/')
    assert response.status_code == 200
    for task in response.data:
        assert task['assignee'] == staff_user.id

def test_manager_can_create_task_for_others(api_client, manager_user, staff_user, get_token):
    token = get_token(manager_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    data = {
        "title": "Task from manager",
        "description": "Assign to staff",
        "status": "pending",
        "priority": "medium",
        "assignee": staff_user.id,
        "owner": manager_user.id
    }
    response = api_client.post('/api/tasks/', data)
    assert response.status_code == 201
    assert response.data['assignee'] == staff_user.id


def test_staff_can_update_own_task(api_client, staff_user, admin_user, get_token):
    task = Task.objects.create(title="Updatable", description="Test", owner=admin_user, assignee=staff_user)
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{task.id}/', {"status": "in_progress"})
    assert response.status_code == 200
    assert response.data['status'] == "in_progress"

def test_staff_cannot_update_task_not_assigned(api_client, staff_user, admin_user, get_token):
    task = Task.objects.create(title="Forbidden", description="Test", owner=admin_user, assignee=admin_user)
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{task.id}/', {"status": "in_progress"})
    assert response.status_code == 404

def test_admin_can_delete_task(api_client, admin_user, staff_user, get_token):
    task = Task.objects.create(title="Deletable", description="To delete", owner=admin_user, assignee=staff_user)
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/tasks/{task.id}/')
    assert response.status_code == 204

def test_staff_cannot_delete_task(api_client, staff_user, admin_user, get_token):
    task = Task.objects.create(title="Not yours", description="Cannot delete", owner=admin_user, assignee=staff_user)
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/tasks/{task.id}/')
    assert response.status_code == 403