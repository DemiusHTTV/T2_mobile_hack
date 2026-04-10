# -*- coding: utf-8 -*-
"""Сериализаторы для AI API."""

from rest_framework import serializers


class AIMessageSerializer(serializers.Serializer):
    """Сериализатор для отправки сообщения в AI."""
    message = serializers.CharField(
        required=True,
        max_length=5000,
        help_text="Текст сообщения для AI"
    )


class AIResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа от AI."""
    success = serializers.BooleanField(help_text="Успешно ли выполнен запрос")
    text = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Текст ответа AI"
    )
    error = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Текст ошибки"
    )
    status_code = serializers.IntegerField(
        required=False,
        help_text="HTTP статус код ответа от API"
    )
