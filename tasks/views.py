from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsAdminManagerOnly, IsAdminManagerOrAssignee, IsAdminManagerOrCreateOwn
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions
from .tasks import send_task_notification_email
from .tasks import send_status_change_email
from rest_framework.exceptions import PermissionDenied


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'manager']

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['title']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'manager']:
            return Task.objects.all()
        return Task.objects.filter(assignee=user)  # Staff chỉ thấy task giao cho họ

    def perform_create(self, serializer):
        user = self.request.user
        assignee = serializer.validated_data.get('assignee')

        if user.role == 'staff' and assignee != user:
            raise PermissionDenied("Staff chỉ có thể gán task cho chính mình.")

        serializer.save()
        send_task_notification_email.delay(serializer.instance.id)


    def perform_update(self, serializer):
        task = self.get_object()
        user = self.request.user

        # Staff chỉ được sửa task giao cho họ
        if user.role == 'staff' and task.assignee != user:
            raise PermissionDenied("Bạn không thể sửa task không phải của mình.")

        updated_task = serializer.save()
        if updated_task.status != task.status:
            send_status_change_email.delay(updated_task.id)

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminManagerOnly()]
        elif self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsAdminManagerOrAssignee()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsAdminManagerOrCreateOwn()]
        return [IsAuthenticated()]


class TaskStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def get(self, request):
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        tasks = Task.objects.filter(created_at__gte=last_7_days)

        data = {
            "pending": tasks.filter(status="pending").count(),
            "in_progress": tasks.filter(status="in_progress").count(),
            "completed": tasks.filter(status="completed").count(),
            "cancelled": tasks.filter(status="cancelled").count(),
        }

        return Response(data)
