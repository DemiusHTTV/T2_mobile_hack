# -*- coding: utf-8 -*-

import requests
import json

# =========================
# НАСТРОЙКИ
# =========================
API_KEY = ""  # вставь сюда
PROJECT_ID = "b1gsdtq8rcvr9irn0bp9"
PROMPT_ID = "fvt36i3obvunn1od9ao3"

URL = "https://ai.api.cloud.yandex.net/v1/responses"


# =========================
# ФУНКЦИЯ ОТПРАВКИ
# =========================
def send_message(message: str):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Api-Key {API_KEY}",
        "OpenAI-Project": PROJECT_ID
    }

    payload = {
        "prompt": {
            "id": PROMPT_ID
        },
        "input": message
    }

    try:
        response = requests.post(
            URL,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8")
        )

        print("\nSTATUS:", response.status_code)

        # Печатаем сырой ответ
        print("\nRAW RESPONSE:")
        print(response.text)

        # Пытаемся распарсить JSON
        try:
            result = response.json()

            print("\nPARSED JSON:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            # Попробуем достать текст
            try:
                text = result["output"][0]["content"][0]["text"]
                print("\nAI TEXT:")
                print(text)
            except:
                print("\nНе удалось достать текст автоматически")

        except:
            print("\nОтвет не JSON")

    except Exception as e:
        print("Ошибка:", e)


# =========================
# ЧАТ В КОНСОЛИ
# =========================
if __name__ == "__main__":
    print("=== ТЕСТ YANDEX AI ===")
    print("Пиши сообщение (exit чтобы выйти)\n")

    while True:
        user_input = input("Ты: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        send_message(user_input)

        print("\n" + "-" * 50)