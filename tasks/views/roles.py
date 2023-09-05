from django.db.models import QuerySet
from django.http import Http404
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Role
from tasks.permissions import IsAdminOnly
from tasks.serializers import RoleCreateSerializer, RoleSerializer


class RoleListView(ListAPIView):
    permission_classes = [IsAdminOnly, permissions.IsAuthenticated]
    serializer_class = RoleSerializer

    def post(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = Role.objects.create(**serializer.data)
        response_data = RoleSerializer(role).data
        return Response(response_data, status=201)

    def get_queryset(self) -> QuerySet:
        return Role.objects.all()


class RoleDetailView(APIView):
    permission_classes = [IsAdminOnly, permissions.IsAuthenticated]

    @staticmethod
    def get_role_or_404(pk: int):
        try:
            role = Role.objects.get(id=pk)
        except Role.DoesNotExist:
            raise Http404

        return role

    def get(self, request, pk: int):
        role = self.get_role_or_404(pk)
        self.check_object_permissions(request, role)
        response_data = RoleSerializer(role).data
        return Response(response_data)

    def post(self, request, pk: int):
        role = self.get_role_or_404(pk)
        self.check_object_permissions(request, role)
        serializer = RoleCreateSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data, status=200)

    def delete(self, request, pk: int):
        role = self.get_role_or_404(pk)
        self.check_object_permissions(request, role)
        role.delete()
        response_data = RoleSerializer(role).data
        return Response(response_data)
