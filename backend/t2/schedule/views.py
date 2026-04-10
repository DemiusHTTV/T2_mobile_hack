from datetime import date as date_type
from datetime import datetime, timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import DailyWorkloadRequirement, Shift, ShiftChangeRequest, WorkloadRequirement
from .permissions import IsAdmin, IsHeadOrAdmin
from .serializers import (
    DailyWorkloadRequirementSerializer,
    ShiftSerializer,
    ShiftChangeRequestSerializer,
    ShiftChangeRequestUpdateSerializer,
    WorkloadRequirementSerializer,
)


def _is_head_or_admin(user) -> bool:
    return bool(user and user.is_authenticated and (getattr(user, "is_admin", False) or getattr(user, "is_head", False)))


class ShiftListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/schedule/shifts/ — список смен (сотрудник: свои; руководитель/admin: все)
    POST /api/schedule/shifts/ — создание смены (сотрудник: только себе)
    """

    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Shift.objects.select_related("employee")
        if not _is_head_or_admin(user):
            qs = qs.filter(employee=user)

        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        employee = serializer.validated_data.get("employee")
        if not _is_head_or_admin(user):
            serializer.save(employee=user)
        else:
            serializer.save(employee=employee or user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response


class ShiftDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    PUT /api/schedule/shifts/{id}/ — редактирование (если не confirmed)
    DELETE /api/schedule/shifts/{id}/ — удаление (если не confirmed)
    """

    queryset = Shift.objects.select_related("employee")
    serializer_class = ShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _can_access(self, user, shift: Shift) -> bool:
        return _is_head_or_admin(user) or shift.employee_id == user.id

    def update(self, request, *args, **kwargs):
        shift: Shift = self.get_object()
        if not self._can_access(request.user, shift):
            return Response({"error": "Доступ запрещён."}, status=status.HTTP_403_FORBIDDEN)
        if shift.status == Shift.Status.CONFIRMED:
            return Response({"error": "Смена подтверждена и не может быть изменена."}, status=status.HTTP_400_BAD_REQUEST)

        # Сотрудник не может подтвердить смену сам
        if not _is_head_or_admin(request.user) and request.data.get("status") == Shift.Status.CONFIRMED:
            return Response({"error": "Только руководитель может подтверждать смены."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        shift: Shift = self.get_object()
        if not self._can_access(request.user, shift):
            return Response({"error": "Доступ запрещён."}, status=status.HTTP_403_FORBIDDEN)
        if shift.status == Shift.Status.CONFIRMED:
            return Response({"error": "Смена подтверждена и не может быть удалена."}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class WorkloadListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/schedule/workloads/ — список нагрузок (все авторизованные)
    POST /api/schedule/workloads/ — создание (только admin)
    """

    queryset = WorkloadRequirement.objects.all()
    serializer_class = WorkloadRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return super().get_permissions()


class WorkloadDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    PUT/DELETE /api/schedule/workloads/{id}/ — только admin
    """

    queryset = WorkloadRequirement.objects.all()
    serializer_class = WorkloadRequirementSerializer
    permission_classes = [IsAdmin]


class DailyWorkloadListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/schedule/workloads/daily/ — список нагрузок на дату (все авторизованные)
    POST /api/schedule/workloads/daily/ — создание (только admin)
    """

    queryset = DailyWorkloadRequirement.objects.all()
    serializer_class = DailyWorkloadRequirementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get("from")
        date_to = self.request.query_params.get("to")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return super().get_permissions()


class DailyWorkloadDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyWorkloadRequirement.objects.all()
    serializer_class = DailyWorkloadRequirementSerializer
    permission_classes = [IsAdmin]


class OptimizeScheduleAPIView(APIView):
    """
    POST /api/schedule/optimize/
    Body: { "from": "YYYY-MM-DD", "to": "YYYY-MM-DD" }

    Генерирует плановые смены по нагрузке.
    Правила:
    - использовать daily workload если есть на дату, иначе weekly workload по weekday
    - распределять по сотрудникам по рейтингу (лучшие чаще), но с балансировкой по нагрузке
    - не назначать >1 смены на сотрудника в день
    - не трогать confirmed смены
    """

    permission_classes = [IsHeadOrAdmin]

    def post(self, request):
        date_from = request.data.get("from")
        date_to = request.data.get("to")
        if not date_from or not date_to:
            return Response({"error": "Нужно указать from/to."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start = datetime.fromisoformat(date_from).date()
            end = datetime.fromisoformat(date_to).date()
        except Exception:
            return Response({"error": "Неверный формат дат. Ожидается YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if end < start:
            return Response({"error": "to не может быть меньше from."}, status=status.HTTP_400_BAD_REQUEST)

        employees = list(User.objects.filter(role=User.RoleChoices.EMPLOYEE, is_active=True).order_by("-rating", "id"))
        if not employees:
            return Response({"error": "Нет сотрудников для распределения."}, status=status.HTTP_400_BAD_REQUEST)

        # Preload workloads
        daily_workloads = list(DailyWorkloadRequirement.objects.filter(date__gte=start, date__lte=end))
        daily_map: dict[date_type, list[DailyWorkloadRequirement]] = {}
        for w in daily_workloads:
            daily_map.setdefault(w.date, []).append(w)

        weekly_workloads = list(WorkloadRequirement.objects.all())
        weekly_map: dict[int, list[WorkloadRequirement]] = {}
        for w in weekly_workloads:
            weekly_map.setdefault(int(w.weekday), []).append(w)

        # Track per-employee assignments
        assigned_total: dict[int, int] = {e.id: 0 for e in employees}

        created = 0
        skipped = 0

        def pick_employee(day: date_type, used_ids: set[int]) -> User | None:
            # Score = rating - 10*assigned_total to balance a bit
            best = None
            best_score = None
            for e in employees:
                if e.id in used_ids:
                    continue
                score = int(getattr(e, "rating", 0)) - 10 * assigned_total.get(e.id, 0)
                if best is None or score > best_score:
                    best = e
                    best_score = score
            return best

        with transaction.atomic():
            day = start
            while day <= end:
                # Determine workload slots for this day
                slots = daily_map.get(day)
                if slots is None:
                    # weekday: Mon=0..Sun=6
                    weekday = (day.weekday())  # python: Mon=0..Sun=6 matches our model
                    slots = weekly_map.get(weekday, [])

                if not slots:
                    day += timedelta(days=1)
                    continue

                # do not overwrite confirmed; also clean old plan shifts for this day (manager/admin view)
                Shift.objects.filter(date=day).exclude(status=Shift.Status.CONFIRMED).delete()

                used_today: set[int] = set()
                for slot in sorted(slots, key=lambda x: x.start_time):
                    required = int(slot.required)
                    for _ in range(required):
                        e = pick_employee(day, used_today)
                        if not e:
                            skipped += 1
                            continue
                        used_today.add(e.id)
                        assigned_total[e.id] = assigned_total.get(e.id, 0) + 1
                        Shift.objects.create(
                            employee=e,
                            date=day,
                            start_time=slot.start_time,
                            end_time=slot.end_time,
                            status=Shift.Status.PLAN,
                        )
                        created += 1

                day += timedelta(days=1)

        return Response({"created": created, "skipped": skipped}, status=status.HTTP_200_OK)


class ChangeRequestListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/schedule/change-requests/ — сотрудник видит свои, менеджер/admin — все
    POST /api/schedule/change-requests/ — создать запрос (сотрудник)
    """

    serializer_class = ShiftChangeRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ShiftChangeRequest.objects.select_related("employee")
        if not _is_head_or_admin(user):
            qs = qs.filter(employee=user)

        status_q = self.request.query_params.get("status")
        if status_q:
            qs = qs.filter(status=status_q)
        return qs

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)


class ChangeRequestDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    PUT /api/schedule/change-requests/{id}/ — изменить статус (manager/admin)
    """

    queryset = ShiftChangeRequest.objects.select_related("employee")
    permission_classes = [IsHeadOrAdmin]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ShiftChangeRequestUpdateSerializer
        return ShiftChangeRequestSerializer
