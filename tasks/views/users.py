from django.db.models import QuerySet
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.filters import UserFilter
from tasks.models import User
from tasks.permissions import IsAdminOnly, IsOwnerOrAdminOnly
from tasks.serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserUpdateAdminSerializer,
    UserUpdateSerializer,
)


class UserListView(ListAPIView):
    permission_classes = [IsAdminOnly, permissions.IsAuthenticated]
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.data)
        response_data = UserSerializer(user).data
        return Response(response_data, status=201)

    def get_queryset(self) -> QuerySet:
        return User.objects.filter(is_active=True)


class UserDetailView(APIView):
    permission_classes = [IsOwnerOrAdminOnly, permissions.IsAuthenticated]

    @staticmethod
    def get_user_or_404(pk: int):
        try:
            user = User.objects.get(id=pk, is_active=True)
        except User.DoesNotExist:
            raise Http404

        return user

    def get(self, request, pk: int):
        user = self.get_user_or_404(pk)
        self.check_object_permissions(request, user)
        response_data = UserSerializer(user).data
        return Response(response_data)

    def post(self, request, pk: int):
        user = self.get_user_or_404(pk)
        self.check_object_permissions(request, user)
        if request.user.is_admin:
            serializer = UserUpdateAdminSerializer(user, data=request.data, partial=True)
        else:
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=200)

    def delete(self, request, pk: int):
        if not request.user.is_admin:
            raise PermissionDenied()

        user = self.get_user_or_404(pk)
        user.is_active = False
        user.updated_by = request.user
        user.save()

        updated = User.objects.get(id=user.id)
        response_data = UserSerializer(updated).data
        return Response(response_data)
