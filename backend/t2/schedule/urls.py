from django.urls import path

from .views import (
    DailyWorkloadDetailAPIView,
    DailyWorkloadListCreateAPIView,
    ChangeRequestDetailAPIView,
    ChangeRequestListCreateAPIView,
    OptimizeScheduleAPIView,
    ShiftDetailAPIView,
    ShiftListCreateAPIView,
    WorkloadDetailAPIView,
    WorkloadListCreateAPIView,
)


urlpatterns = [
    path("shifts/", ShiftListCreateAPIView.as_view(), name="shift_list_create"),
    path("shifts/<int:pk>/", ShiftDetailAPIView.as_view(), name="shift_detail"),
    path("workloads/", WorkloadListCreateAPIView.as_view(), name="workload_list_create"),
    path("workloads/<int:pk>/", WorkloadDetailAPIView.as_view(), name="workload_detail"),
    path("workloads/daily/", DailyWorkloadListCreateAPIView.as_view(), name="daily_workload_list_create"),
    path("workloads/daily/<int:pk>/", DailyWorkloadDetailAPIView.as_view(), name="daily_workload_detail"),
    path("optimize/", OptimizeScheduleAPIView.as_view(), name="optimize"),
    path("change-requests/", ChangeRequestListCreateAPIView.as_view(), name="change_request_list_create"),
    path("change-requests/<int:pk>/", ChangeRequestDetailAPIView.as_view(), name="change_request_detail"),
]
