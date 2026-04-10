# -*- coding: utf-8 -*-
"""API views для работы с Yandex AI."""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from .yandex_ai_service import ai_service
from .serializers import AIMessageSerializer, AIResponseSerializer


class AIChatAPIView(APIView):
    """
    Endpoint для отправки сообщений в Yandex AI.
    POST /api/ai/chat/
    
    Принимает:
        - message: текст сообщения
    
    Возвращает:
        - success: успешно ли выполнен запрос
        - text: ответ AI
        - error: ошибка (если есть)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AIMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data['message']
        
        # Вызываем AI сервис
        result = ai_service.send_message(message)

        if result.get('success'):
            response_serializer = AIResponseSerializer(data=result)
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)


class AIChatAnonymousAPIView(APIView):
    """
    Endpoint для отправки сообщений в Yandex AI без авторизации.
    POST /api/ai/chat/public/
    
    Внимание: этот endpoint открытый, используйте rate limiting в production.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AIMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data['message']
        
        # Вызываем AI сервис
        result = ai_service.send_message(message)

        if result.get('success'):
            response_serializer = AIResponseSerializer(data=result)
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)


class AIStatusAPIView(APIView):
    """
    Проверка статуса AI сервиса.
    GET /api/ai/status/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        is_configured = ai_service.is_configured()
        return Response({
            "configured": is_configured,
            "service": "Yandex AI"
        })
