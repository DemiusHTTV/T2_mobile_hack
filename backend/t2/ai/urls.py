# -*- coding: utf-8 -*-
"""URL маршруты для AI API."""

from django.urls import path
from .views import AIChatAPIView, AIChatAnonymousAPIView, AIStatusAPIView

urlpatterns = [
    path('chat/', AIChatAPIView.as_view(), name='ai_chat'),
    path('chat/public/', AIChatAnonymousAPIView.as_view(), name='ai_chat_public'),
    path('status/', AIStatusAPIView.as_view(), name='ai_status'),
]
