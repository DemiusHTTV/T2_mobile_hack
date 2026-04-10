from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    """Модель организации."""
    name = models.CharField(max_length=255, verbose_name="Название организации")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name


class Department(models.Model):
    """Модель подразделения."""
    name = models.CharField(max_length=255, verbose_name="Название подразделения")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name="Организация"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class User(AbstractUser):
    """Кастомная модель пользователя с ролями."""

    class RoleChoices(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        HEAD = 'head', 'Руководитель'
        EMPLOYEE = 'employee', 'Сотрудник'

    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.EMPLOYEE,
        verbose_name="Роль"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Подразделение"
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Организация"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.RoleChoices.ADMIN

    @property
    def is_head(self):
        return self.role == self.RoleChoices.HEAD

    @property
    def is_employee(self):
        return self.role == self.RoleChoices.EMPLOYEE
