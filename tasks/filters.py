from django_filters import rest_framework as filters

from tasks.models import TASK_STATUS_CHOICES, Task, User


class UserFilter(filters.FilterSet):
    email = filters.CharFilter(field_name="email")

    class Meta:
        model = User
        fields = [
            "email",
        ]


class TaskFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", method="filter_title")
    status = filters.ChoiceFilter(choices=TASK_STATUS_CHOICES)
    due_date = filters.DateFilter(field_name="due_date")
    due_date_from = filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_to = filters.DateFilter(field_name="due_date", lookup_expr="lte")

    def filter_title(self, queryset, name, value):
        return queryset.filter(title__icontains=value)

    class Meta:
        model = Task
        fields = [
            "title",
            "status",
            "due_date",
        ]
