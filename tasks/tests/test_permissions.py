import pytest
from rest_framework.test import APIClient
from users.models import User
from tasks.models import Task

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
def get_token(api_client):
    def _get_token(user):
        password = '123456' if user.role == 'admin' else ('123456abc#' if user.role == 'manager' else 'password')
        response = api_client.post('/api/token/', {'username': user.username, 'password': password})
        return response.data['access']
    return _get_token

@pytest.fixture
def sample_task(admin_user, staff_user):
    return Task.objects.create(title="Sample Task", description="Test task", owner=admin_user, assignee=staff_user)

# -------------------- TEST PHÂN QUYỀN ------------------------

def test_admin_can_delete_task(api_client, admin_user, get_token, sample_task):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/tasks/{sample_task.id}/')
    assert response.status_code == 204

def test_manager_can_delete_task(api_client, manager_user, get_token, sample_task):
    token = get_token(manager_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/tasks/{sample_task.id}/')
    assert response.status_code == 204

def test_staff_cannot_delete_task(api_client, staff_user, get_token, sample_task):
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.delete(f'/api/tasks/{sample_task.id}/')
    assert response.status_code == 403

def test_admin_can_update_any_task(api_client, admin_user, get_token, sample_task):
    token = get_token(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{sample_task.id}/', {'status': 'in_progress'})
    assert response.status_code == 200

def test_manager_can_update_any_task(api_client, manager_user, get_token, sample_task):
    token = get_token(manager_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{sample_task.id}/', {'status': 'in_progress'})
    assert response.status_code == 200

def test_staff_can_update_own_assigned_task(api_client, staff_user, get_token, sample_task):
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{sample_task.id}/', {'status': 'completed'})
    assert response.status_code == 200

def test_staff_cannot_update_task_not_assigned(api_client, staff_user, admin_user, get_token):
    task = Task.objects.create(title="Not Yours", description="Forbidden", owner=admin_user, assignee=admin_user)
    token = get_token(staff_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.patch(f'/api/tasks/{task.id}/', {'status': 'completed'})
    assert response.status_code == 404
