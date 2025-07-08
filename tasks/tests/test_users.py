import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserEndpoints:

    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='trinhxuanphuong39@gmail.com',
            password='123456',
            role='admin',
            is_staff=True,
        )
        self.manager = User.objects.create_user(
            username='manager_test',
            email='txphuonggg@gmail.com',
            password='123456abc#',
            role='manager',
        )
        self.staff = User.objects.create_user(
            username='staff_test',
            email='himinngaming@gmail.com',
            password='password',
            role='staff',
        )

    def get_token(self, username, password):
        res = self.client.post("/api/token/", {
            "username": username,
            "password": password
        })
        return res.data.get("access")

    def test_register_as_anonymous(self):
        response = self.client.post("/api/users/register/", {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "role": "admin"
        })
        assert response.status_code == 201
        assert response.data["role"] == "staff"  # Bị ép thành staff nếu không phải admin

    def test_register_as_admin(self):
        token = self.get_token("admin_test", "123456")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.post("/api/users/register/", {
            "username": "anotheruser",
            "email": "another@example.com",
            "password": "adminpass",
            "role": "manager"
        })

        assert response.status_code == 201
        assert response.data["role"] == "manager"

    def test_login_invalid_credentials(self):
        response = self.client.post("/api/token/", {
            "username": "admin_test",
            "password": "wrongpass"
        })
        assert response.status_code == 401

    def test_login_success(self):
        response = self.client.post("/api/token/", {
            "username": "staff_test",
            "password": "password"
        })
        assert response.status_code == 200
        assert "access" in response.data

    def test_user_me_authenticated(self):
        token = self.get_token("manager_test", "123456abc#")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get("/api/users/me/")
        assert response.status_code == 200
        assert response.data["username"] == "manager_test"
        assert "password" not in response.data

    def test_user_me_unauthenticated(self):
        response = self.client.get("/api/users/me/")
        assert response.status_code == 401

    def test_user_register_with_duplicate_email(self):
        token = self.get_token("admin_test", "123456")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="abc123",
            role="staff"
        )
        # Thử đăng ký với email đã tồn tại
        response = self.client.post("/api/users/register/", {
            "username": "newuser2",
            "email": "user2@example.com",  # trùng email
            "password": "pass123",
            "role": "staff"
        })
        assert response.status_code == 400
