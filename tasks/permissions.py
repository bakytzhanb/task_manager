from typing import Any

from django.views import View
from rest_framework import permissions
from rest_framework.request import Request

from tasks.models import Task, User


class IsOwnerOrAssignedOrAdminOnly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: Task) -> bool:
        if any(
            [
                obj.created_by == request.user,
                obj.assigned_to == request.user,
                request.user.is_admin,
            ]
        ):
            return True

        return False


class IsOwnerOrAdminOnly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: View, obj: User) -> bool:
        if request.user.is_admin or obj == request.user:
            return True
        return False


class IsAdminOnly(permissions.BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        if request.user.is_admin:
            return True
        return False

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        if request.user.is_admin:
            return True
        return False
