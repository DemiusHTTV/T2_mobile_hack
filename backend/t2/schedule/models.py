from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Shift(models.Model):
    class Status(models.TextChoices):
        PLAN = "plan", "Plan"
        FACT = "fact", "Fact"
        CONFIRMED = "confirmed", "Confirmed"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shifts"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PLAN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "start_time"]
        verbose_name = "Смена"
        verbose_name_plural = "Смены"
        indexes = [
            models.Index(fields=["employee", "date"], name="shift_employee_date_idx"),
        ]

    def clean(self) -> None:
        super().clean()

        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "Время окончания должно быть позже времени начала."})

        today = timezone.localdate()
        if self.date and self.date < today:
            raise ValidationError({"date": "Нельзя создавать смену на прошедшую дату."})

        if self.date and self.date > today + timedelta(days=14):
            raise ValidationError({"date": "Нельзя создавать смену больше чем на 2 недели вперёд."})

        if self.employee_id and self.date and self.start_time and self.end_time:
            overlap_qs = Shift.objects.filter(employee_id=self.employee_id, date=self.date)
            if self.pk:
                overlap_qs = overlap_qs.exclude(pk=self.pk)

            overlap_qs = overlap_qs.filter(
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
            )
            if overlap_qs.exists():
                raise ValidationError("Смена пересекается с уже существующей сменой.")

    def __str__(self) -> str:
        return f"Shift({self.employee_id}, {self.date} {self.start_time}-{self.end_time})"
