from django.db.models import Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.filters import TaskFilter
from tasks.helpers import celery_send_email
from tasks.models import Task
from tasks.permissions import IsOwnerOrAssignedOrAdminOnly
from tasks.serializers import TaskCreateSerializer, TaskSerializer


class TaskListView(ListAPIView):
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self) -> QuerySet:
        tasks = Task.objects.all()
        if not self.request.user.is_admin:
            tasks = tasks.filter(
                Q(created_by=self.request.user) | Q(assigned_to=self.request.user)
            )

        return tasks

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=self.request.user)

        return Response(serializer.data, status=201)


class TaskDetailView(APIView):
    permission_classes = [IsOwnerOrAssignedOrAdminOnly, permissions.IsAuthenticated]

    def get(self, request, pk: int):
        task = Task.objects.get(id=pk)
        self.check_object_permissions(request, task)
        response_data = TaskSerializer(task).data
        return Response(response_data)

    def post(self, request, pk: int):
        task = Task.objects.get(id=pk)
        initial_assigned = task.assigned_to

        self.check_object_permissions(request, task)
        serializer = TaskCreateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)

        if assigned_to := serializer.validated_data.get("assigned_to"):
            if assigned_to != initial_assigned:
                celery_send_email.delay(
                    subject="You have been assigned a new task",
                    message=f"Task id - {task.id}",
                    target_mail=assigned_to.email,
                )

        return Response(serializer.data, status=200)

    def delete(self, request, pk: int):
        task = Task.objects.get(id=pk)
        self.check_object_permissions(request, task)
        task.delete()
        response_data = TaskSerializer(task).data
        return Response(response_data)
