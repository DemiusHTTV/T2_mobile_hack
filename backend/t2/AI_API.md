# AI API Документация

## Обзор

Интеграция Yandex AI в Django бэкенд позволяет отправлять сообщения в Yandex GPT через REST API.

## Настройка

### 1. Получение API ключа

1. Зарегистрируйтесь на [Yandex Cloud](https://cloud.yandex.ru/)
2. Создайте сервисный аккаунт
3. Получите API ключ
4. Настройте Prompt ID в Yandex AI

### 2. Конфигурация

В файле `t2/settings.py` укажите:

```python
# Yandex AI Settings
YANDEX_AI_API_KEY = "ваш_API_ключ"  # вставьте сюда свой API ключ
YANDEX_AI_PROJECT_ID = "b1gsdtq8rcvr9irn0bp9"
YANDEX_AI_PROMPT_ID = "fvt36i3obvunn1od9ao3"
```

## API Endpoints

### 1. Отправка сообщения (с авторизацией)

**URL:** `POST /api/ai/chat/`

**Требования:** JWT аутентификация

**Запрос:**
```json
{
  "message": "Текст сообщения"
}
```

**Ответ (успех):**
```json
{
  "success": true,
  "text": "Ответ от AI",
  "error": null,
  "status_code": 200
}
```

**Ответ (ошибка):**
```json
{
  "success": false,
  "error": "Текст ошибки",
  "status_code": 502
}
```

### 2. Публичная отправка сообщения (без авторизации)

**URL:** `POST /api/ai/chat/public/`

**Требования:** Нет

⚠️ **Внимание:** Этот endpoint открытый! В production используйте rate limiting.

**Запрос и ответ** аналогичны endpoint'у с авторизацией.

### 3. Проверка статуса AI сервиса

**URL:** `GET /api/ai/status/`

**Требования:** JWT аутентификация

**Ответ:**
```json
{
  "configured": true,
  "service": "Yandex AI"
}
```

## Примеры использования

### Пример с curl (публичный endpoint):

```bash
curl -X POST http://localhost:8000/api/ai/chat/public/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет, как дела?"}'
```

### Пример с JavaScript (fetch):

```javascript
// С авторизацией
const response = await fetch('http://localhost:8000/api/ai/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`
  },
  body: JSON.stringify({
    message: 'Привет, AI!'
  })
});

const data = await response.json();
console.log(data.text);
```

### Пример с Python (requests):

```python
import requests

# Публичный endpoint
response = requests.post(
    'http://localhost:8000/api/ai/chat/public/',
    json={'message': 'Привет!'}
)

print(response.json()['text'])
```

## Структура AI приложения

```
ai/
├── __init__.py
├── apps.py                 # Конфигурация приложения
├── views.py                # API views (эндпоинты)
├── urls.py                 # Маршруты URL
├── serializers.py          # Сериализаторы DRF
├── yandex_ai_service.py    # Сервис для работы с Yandex AI
└── tests.py                # Тесты
```

## Архитектура

```
Клиент
    ↓ HTTP POST /api/ai/chat/
Django View (AIChatAPIView)
    ↓ Валидация через AIMessageSerializer
YandexAIService.send_message()
    ↓ HTTP запрос к Yandex Cloud AI
Yandex AI API
    ↓ JSON ответ
YandexAIService
    ↓ Извлечение текста
Django View
    ↓ Сериализация через AIResponseSerializer
Клиент
```

## Безопасность

- **Авторизованные endpoints** (`/api/ai/chat/`) - требуют JWT токен
- **Публичные endpoints** (`/api/ai/chat/public/`) - доступны всем, используйте rate limiting в production
- **API ключ** хранится в `settings.py`, не коммитьте его в git!

## Troubleshooting

### Ошибка "Yandex AI не настроен"

Убедитесь, что в `settings.py` указаны:
- `YANDEX_AI_API_KEY`
- `YANDEX_AI_PROJECT_ID`
- `YANDEX_AI_PROMPT_ID`

### Ошибка "Превышено время ожидания"

Проверьте:
- Подключение к интернету
- Доступность Yandex Cloud API
- Корректность API ключа

### Ошибка 401 Unauthorized

Получите JWT токен через `/api/token/`:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

Используйте `access` токен в заголовке `Authorization: Bearer <token>`
