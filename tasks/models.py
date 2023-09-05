from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from tasks.constants import SystemRole

TASK_STATUS_CHOICES = (("N", "New"), ("P", "Planning"), ("I", "In progress"), ("C", "Completed"))


class Role(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str, roles: list[str] | None = None, **extra_fields
    ):
        if not email:
            raise ValueError("Email is required for User")

        if not password:
            raise ValueError("Password is required for User")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        user_roles = None
        if roles:
            user_roles = Role.objects.filter(name__in=roles)

        if user_roles:
            user.roles.set(user_roles)

        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, roles=[SystemRole.ADMIN], **extra_fields)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=250, blank=True)
    last_name = models.CharField(max_length=250, blank=True)
    is_active = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    objects = UserManager()

    def get_full_name(self) -> str | None:
        if self.first_name and self.last_name:
            return f"{self.first_name}  {self.last_name}"
        return None

    @property
    def is_admin(self) -> bool:
        admin_role = Role.objects.get(name=SystemRole.ADMIN)
        return self.roles.contains(admin_role)


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    status = models.CharField(max_length=1, choices=TASK_STATUS_CHOICES, default="N")
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="updated_tasks",
    )
