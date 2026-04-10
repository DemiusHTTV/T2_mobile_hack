from django.contrib import admin

from .models import Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "date", "start_time", "end_time", "status")
    list_filter = ("status", "date")
    search_fields = ("employee__username", "employee__email")

