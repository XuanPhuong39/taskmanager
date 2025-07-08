import os
import django
from django.urls import get_resolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # thay nếu tên khác
django.setup()  # BẮT BUỘC phải gọi dòng này trước

resolver = get_resolver()

for pattern in resolver.url_patterns:
    print(pattern)
