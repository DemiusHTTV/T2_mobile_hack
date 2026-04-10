from django.urls import path

from . import views


urlpatterns = [
    path("shifts/", views.shifts_collection, name="shifts_collection"),
    path("shifts/<int:shift_id>/", views.shift_detail, name="shift_detail"),
]

