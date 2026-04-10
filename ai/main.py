import requests
import json
import logging
from typing import Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YandexCloudAI:
    def __init__(self, api_key: str, project_id: str, prompt_id: str):
        self.api_url = "https://ai.api.cloud.yandex.net/v1/responses"
        self.api_key = api_key
        self.project_id = project_id
        self.prompt_id = prompt_id
        
    def send_message(self, user_input: str) -> Dict[str, Any]:
        """Отправка сообщения в Yandex Cloud AI и получение ответа"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.api_key}",
            "OpenAI-Project": self.project_id
        }
        
        payload = {
            "prompt": {"id": self.prompt_id},
            "input": user_input
        }
        
        try:
            logger.info(f"Отправка запроса с сообщением: {user_input[:50]}...")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30  # Таймаут 30 секунд
            )
            
            response.raise_for_status()  # Выбросит исключение для 4xx/5xx
            
            result = response.json()
            logger.info("Успешно получен ответ от API")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Таймаут соединения")
            return {"error": "Timeout", "message": "Сервер не ответил за 30 секунд"}
        except requests.exceptions.ConnectionError:
            logger.error("Ошибка соединения")
            return {"error": "ConnectionError", "message": "Не удалось подключиться к API"}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP ошибка: {e}")
            return {"error": "HTTPError", "status_code": response.status_code, "text": response.text}
        except json.JSONDecodeError:
            logger.error("Ошибка парсинга JSON")
            return {"error": "JSONDecodeError", "response_text": response.text}
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return {"error": "UnknownError", "message": str(e)}
    
    def send_schedule_query(self, query: str) -> Dict[str, Any]:
        """Специализированный метод для запросов по расписанию"""
        
        full_message = f"""
        Ты консультант по расписанию в Smartsheet.
        Запрос сотрудника: {query}
        
        Ответь, проанализировав:
        1. Почему сотрудник поставлен в это время
        2. Возможность изменения
        3. Отправь уведомление менеджеру если нужно
        """
        
        return self.send_message(full_message)

# Использование
if __name__ == "__main__":
    # Инициализация клиента
    client = YandexCloudAI(
        api_key="<API_key_value>",  # Замените на реальный ключ
        project_id="b1gsdtq8rcvr9irn0bp9",
        prompt_id="fvt36i3obvunn1od9ao3"
    )
    
    # Примеры запросов
    queries = [
        "ПОЧЕМУ Я ПОСТАВЛЕН на пятницу?",
        "поставь меня на больше утренних смен",
        "почему у меня 3 смены подряд?"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"ЗАПРОС: {query}")
        print('='*60)
        
        result = client.send_schedule_query(query)
        
        # Вывод результата в читаемом формате
        if "error" in result:
            print(f"❌ ОШИБКА: {result.get('message', 'Неизвестная ошибка')}")
        else:
            print("✅ ОТВЕТ:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        print("\n" + "-"*60)