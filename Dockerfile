# Sử dụng image Python chính thức
FROM python:3.11

# Không sinh ra file .pyc và in ra stdout ngay
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tạo thư mục làm việc trong container
WORKDIR /app

# Copy file requirements trước để tận dụng cache khi build
COPY requirements.txt .

# Cài các package cần thiết
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy toàn bộ project vào container
COPY . .

# Chạy gunicorn để start server
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
