from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from tasks.models import Role, Task, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RoleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ("created_at", "updated_at", "updated_by")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserCreateSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = User
        exclude = ("created_at", "updated_at", "updated_by")


class UserUpdateAdminSerializer(serializers.ModelSerializer):
    def validate_password(self, value):
        return make_password(value)

    class Meta:
        model = User
        exclude = ("created_at", "updated_at", "updated_by")


class UserUpdateSerializer(UserUpdateAdminSerializer):
    class Meta:
        model = User
        exclude = ("created_at", "updated_at", "updated_by", "roles", "is_active")


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ("created_by", "created_at", "updated_at", "updated_by")
