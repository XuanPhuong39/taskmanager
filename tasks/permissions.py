from rest_framework.permissions import BasePermission

class IsAdminManagerOrCreateOwn(BasePermission):
    def has_permission(self, request, view):
        # Cho phép tất cả user được tạo task
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return request.user.role in ['admin', 'manager'] or obj.owner == request.user
        return True


class IsAdminManagerOrAssignee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role in ['admin', 'manager']
            or obj.assignee == request.user
        )
class IsAdminManagerOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'manager']
