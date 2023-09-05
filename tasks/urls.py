from django.urls import path

from .views.roles import RoleDetailView, RoleListView
from .views.tasks import TaskDetailView, TaskListView
from .views.users import UserDetailView, UserListView

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="tasks_list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task_detail"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    path("roles/", RoleListView.as_view(), name="role_list"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role_detail"),
]
