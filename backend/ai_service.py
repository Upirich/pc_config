from openai import OpenAI
from typing import Dict, List
import logging

client = OpenAI(
    api_key="sk-KZBayWeUNOHz0lGu1xOEVxVizGudZ5JF",
    base_url="https://api.proxyapi.ru/openai/v1",
)

user_messages: Dict[int, List[dict]] = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Ты ассистент, который отвечает только на вопросы, связанные с компьютерами, "
        "сборкой ПК, комплектующими, апгрейдом, бюджетами, игровыми и офисными конфигурациями. "
        "Если вопрос не по теме, politely откажись отвечать."
    ),
}


def chat_with_gpt(user_input: str, user_id: int) -> str:
    try:
        if user_id not in user_messages:
            user_messages[user_id] = [SYSTEM_PROMPT]

        user_messages[user_id].append({"role": "user", "content": user_input})

        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=user_messages[user_id]
        )

        response = chat_completion.choices[0].message.content
        user_messages[user_id].append({"role": "assistant", "content": response})
        return response

    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI:")
        return "❌ Произошла ошибка при обработке запроса к ИИ."


def handle_ai_request(prompt: str, user_id: int) -> str:
    return chat_with_gpt(prompt, user_id)
