from django.contrib import admin

from .models import DailyWorkloadRequirement, Shift, WorkloadRequirement


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "date", "start_time", "end_time", "status")
    list_filter = ("status", "date")
    search_fields = ("employee__username", "employee__email")


@admin.register(WorkloadRequirement)
class WorkloadRequirementAdmin(admin.ModelAdmin):
    list_display = ("id", "weekday", "start_time", "end_time", "required")
    list_filter = ("weekday",)


@admin.register(DailyWorkloadRequirement)
class DailyWorkloadRequirementAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "start_time", "end_time", "required")
    list_filter = ("date",)
