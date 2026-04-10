from __future__ import annotations

import json
from datetime import date as date_type
from datetime import time as time_type
from functools import wraps

from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_http_methods

from .models import Shift


def _is_manager(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


def api_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({"error": "Требуется авторизация."}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped


def _parse_json(request: HttpRequest) -> dict:
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError("Некорректный JSON в теле запроса.") from exc


def _serialize_shift(shift: Shift) -> dict:
    return {
        "id": shift.id,
        "employee_id": shift.employee_id,
        "employee_username": getattr(shift.employee, "username", None),
        "date": shift.date.isoformat(),
        "start_time": shift.start_time.strftime("%H:%M"),
        "end_time": shift.end_time.strftime("%H:%M"),
        "status": shift.status,
        "created_at": shift.created_at.isoformat(),
        "updated_at": shift.updated_at.isoformat(),
    }


def _coerce_date(value) -> date_type | None:
    if value is None:
        return None
    if isinstance(value, date_type):
        return value
    if isinstance(value, str):
        parsed = parse_date(value)
        if parsed:
            return parsed
    raise ValidationError({"date": "Неверная дата. Ожидается YYYY-MM-DD."})


def _coerce_time(value, field_name: str) -> time_type | None:
    if value is None:
        return None
    if isinstance(value, time_type):
        return value
    if isinstance(value, str):
        parsed = parse_time(value)
        if parsed:
            return parsed
    raise ValidationError({field_name: "Неверное время. Ожидается HH:MM[:SS]."})


@api_login_required
@require_http_methods(["GET", "POST"])
def shifts_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        qs = Shift.objects.select_related("employee")
        if not _is_manager(request.user):
            qs = qs.filter(employee=request.user)

        try:
            date_from = request.GET.get("from")
            date_to = request.GET.get("to")
            if date_from:
                qs = qs.filter(date__gte=_coerce_date(date_from))
            if date_to:
                qs = qs.filter(date__lte=_coerce_date(date_to))
        except ValidationError as exc:
            return JsonResponse(
                {"error": exc.message_dict if hasattr(exc, "message_dict") else str(exc)},
                status=400,
            )

        return JsonResponse({"results": [_serialize_shift(s) for s in qs]}, status=200)

    # POST
    try:
        payload = _parse_json(request)
    except ValidationError as exc:
        return JsonResponse(
            {"error": exc.message_dict if hasattr(exc, "message_dict") else str(exc)},
            status=400,
        )
    employee_id = payload.get("employee_id")

    shift = Shift(
        employee_id=employee_id if (employee_id and _is_manager(request.user)) else request.user.id,
        date=_coerce_date(payload.get("date")),
        start_time=_coerce_time(payload.get("start_time"), "start_time"),
        end_time=_coerce_time(payload.get("end_time"), "end_time"),
        status=payload.get("status") or Shift.Status.PLAN,
    )

    try:
        shift.full_clean()
    except ValidationError as exc:
        return JsonResponse({"error": exc.message_dict if hasattr(exc, "message_dict") else str(exc)}, status=400)

    shift.save()
    shift.refresh_from_db()
    return JsonResponse(_serialize_shift(shift), status=201)


@api_login_required
@require_http_methods(["PUT", "DELETE"])
def shift_detail(request: HttpRequest, shift_id: int) -> HttpResponse:
    shift = get_object_or_404(Shift.objects.select_related("employee"), pk=shift_id)

    if not (_is_manager(request.user) or shift.employee_id == request.user.id):
        return JsonResponse({"error": "Доступ запрещён."}, status=403)

    if shift.status == Shift.Status.CONFIRMED:
        return JsonResponse({"error": "Смена подтверждена и не может быть изменена."}, status=400)

    if request.method == "DELETE":
        shift.delete()
        return HttpResponse(status=204)

    # PUT
    try:
        payload = _parse_json(request)
    except ValidationError as exc:
        return JsonResponse(
            {"error": exc.message_dict if hasattr(exc, "message_dict") else str(exc)},
            status=400,
        )

    if "status" in payload:
        new_status = payload.get("status")
        if new_status == Shift.Status.CONFIRMED and not _is_manager(request.user):
            return JsonResponse({"error": "Только руководитель может подтверждать смены."}, status=403)
        shift.status = new_status

    if "date" in payload:
        shift.date = _coerce_date(payload.get("date"))

    if "start_time" in payload:
        shift.start_time = _coerce_time(payload.get("start_time"), "start_time")

    if "end_time" in payload:
        shift.end_time = _coerce_time(payload.get("end_time"), "end_time")

    try:
        shift.full_clean()
    except ValidationError as exc:
        return JsonResponse({"error": exc.message_dict if hasattr(exc, "message_dict") else str(exc)}, status=400)

    shift.save(update_fields=["date", "start_time", "end_time", "status", "updated_at"])
    shift.refresh_from_db()
    return JsonResponse(_serialize_shift(shift), status=200)
