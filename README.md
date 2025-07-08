# Task Manager Backend API

Hệ thống quản lý công việc sử dụng Django REST Framework, JWT, Celery, Redis và Docker. Gồm 5 module:

- Quản lý người dùng và phân quyền theo vai trò (Admin / Manager / Staff)
- Quản lý công việc (Task)
- Thống kê công việc 7 ngày gần nhất
- Gửi mail khi tạo và thay đổi trạng thái công việc
- Nhắc nhở deadline hàng ngày lúc 8h sáng

---

## Tech Stack
- Python 3.11
- Django + DRF
- SimpleJWT
- PostgreSQL
- Celery + Redis
- drf-spectacular (Swagger UI)
- Docker Compose

---

## Hướng dẫn cài đặt

### 1. Clone và build bằng Docker

```bash
git clone <repo-url>
cd taskmanager
docker compose up -d --build
```

### 2. Tạo superuser (nếu cần)

```bash
docker compose exec web python manage.py createsuperuser
```

### 3. Truy cập hệ thống

| Thành phần | URL                              |
|------------|----------------------------------|
| Swagger    | http://localhost:8000/api/docs/  |
| Admin      | http://localhost:8000/admin/     |
| API Token  | http://localhost:8000/api/token/ |

---

## Phân quyền người dùng

| Vai trò  | Quyền                                                                 |
|----------|-----------------------------------------------------------------------|
| Admin    | Toàn quyền hệ thống, tạo user/ task, xoá, cập nhật mọi thứ            |
| Manager  | Tạo/ xem/ sửa/ xoá/ gán task cho bất kỳ ai                            |
| Staff    | Tạo task cho chính mình, chỉ xem/ sửa task của mình                   |

### Tài khoản mẫu

| Username    | Password  | Role     |
|-------------|-----------|----------|
| admin2      | 123456    | admin    |
| managertest | 123456abc#| manager  |
| user22      | password  | staff    |

---

## Xác thực JWT

### Đăng nhập:

```
POST /api/token/
{
  "username": "admin2",
  "password": "123456"
}
```

### Lấy thông tin người dùng:

```
GET /api/users/me/
Headers: Authorization: Bearer <access_token>
```

---

## API Chính

### Task CRUD: `/api/tasks/`

- `GET /api/tasks/` – xem danh sách task
- `POST /api/tasks/` – tạo task
- `PUT /api/tasks/<id>/` – cập nhật task
- `DELETE /api/tasks/<id>/` – xoá task

> Lọc theo: `?status=...&priority=...`  
> Tìm kiếm: `?search=keyword` (tìm theo title)

### Thống kê: `/api/stats/`

- `GET /api/stats/`
- Chỉ Admin & Manager được truy cập
- Trả về số lượng task theo trạng thái trong 7 ngày gần nhất:
  ```json
  {
    "pending": 29,
    "in_progress": 21,
    "completed": 15,
    "cancelled": 11
  }
  ```

---

## Tác vụ nền (Celery)

### Gửi email khi:

- Tạo mới task
- Thay đổi trạng thái

### Gửi email nhắc deadline:

- Mỗi ngày 8h sáng
- Gửi mail cho `assignee` nếu task đến hạn trong 24h

---
## Unit Test

Chạy lệnh:

```bash
docker compose exec web pytest
```

---

## Docker Services

| Service | Description        |
|---------|--------------------|
| `web`   | Django API server  |
| `db`    | PostgreSQL database|
| `redis` | Redis broker       |
| `worker`| Celery worker      |
| `beat`  | Celery Beat        |

Khởi động:

```bash
docker compose up -d --build
```

---

## Hoàn tất

Dự án đã triển khai đầy đủ các chức năng:
- [x] Quản lý người dùng & phân quyền
- [x] Quản lý công việc: CRUD, lọc, tìm kiếm
- [x] Xác thực JWT
- [x] Celery gửi mail khi tạo & cập nhật task
- [x] Celery Beat nhắc deadline lúc 8h sáng
- [x] API thống kê /api/stats/
- [x] Swagger UI
- [x] Docker hoá toàn bộ hệ thống

---

## Thư mục chính

```
taskmanager/
├── config/                 # Cấu hình Django
├── tasks/                 # App quản lý Task
├── users/                 # App người dùng & phân quyền
├── docker-compose.yml     # Docker Compose config
├── Dockerfile             # Web Dockerfile
├── requirements.txt
└── README.md
```