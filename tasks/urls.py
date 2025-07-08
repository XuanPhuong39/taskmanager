from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskStatsView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', TaskStatsView.as_view(), name='task-stats'),
]
