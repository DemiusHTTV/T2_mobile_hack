# -*- coding: utf-8 -*-
"""Сервис для работы с Yandex AI."""

import requests
import json
from django.conf import settings


class YandexAIService:
    """Клиент для Yandex AI API."""

    def __init__(self):
        self.api_key = getattr(settings, 'YANDEX_AI_API_KEY', '')
        self.project_id = getattr(settings, 'YANDEX_AI_PROJECT_ID', '')
        self.prompt_id = getattr(settings, 'YANDEX_AI_PROMPT_ID', '')
        self.url = "https://ai.api.cloud.yandex.net/v1/responses"

    def is_configured(self):
        """Проверка, настроен ли сервис."""
        return bool(self.api_key and self.project_id and self.prompt_id)

    def send_message(self, message: str) -> dict:
        """
        Отправка сообщения в Yandex AI.
        
        Args:
            message: Текст сообщения
            
        Returns:
            dict: Ответ от API с текстом и метаданными
        """
        if not self.is_configured():
            return {
                "error": "Yandex AI не настроен. Проверьте настройки YANDEX_AI_* в settings.py",
                "success": False
            }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Api-Key {self.api_key}",
            "OpenAI-Project": self.project_id
        }

        payload = {
            "prompt": {
                "id": self.prompt_id
            },
            "input": message
        }

        try:
            response = requests.post(
                self.url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "error": f"Ошибка API: {response.status_code}",
                    "status_code": response.status_code,
                    "raw_response": response.text,
                    "success": False
                }

            result = response.json()

            # Извлекаем текст ответа
            ai_text = None
            try:
                ai_text = result["output"][0]["content"][0]["text"]
            except (KeyError, IndexError, TypeError):
                ai_text = result.get("output", str(result))

            return {
                "text": ai_text,
                "raw_response": result,
                "success": True,
                "status_code": response.status_code
            }

        except requests.exceptions.Timeout:
            return {
                "error": "Превышено время ожидания ответа от AI",
                "success": False
            }
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Ошибка соединения: {str(e)}",
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Неизвестная ошибка: {str(e)}",
                "success": False
            }


# Singleton instance
ai_service = YandexAIService()
