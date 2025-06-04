from rest_framework.permissions import BasePermission

class IsAdminUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role_id == 'admin'

class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role_id == 'admin' or obj.id == request.user.id

    def has_permission(self, request, view):
        return request.user.is_authenticated
