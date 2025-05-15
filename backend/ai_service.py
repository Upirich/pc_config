from openai import OpenAI
from typing import Dict, List
import logging
from sqlalchemy.orm import Session
from models import Component
from schemas import Complect, FinalAnswer
import json

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


def get_components_from_db(db: Session) -> List[Complect]:
    components = db.query(Component).all()
    return [
        Complect(
            id=component.id,
            name=component.name,
            type=component.type,
            price=component.price,
            description=component.description,
        )
        for component in components
    ]


def chat_with_gpt(user_input: str, user_id: int, db: Session) -> FinalAnswer:
    try:
        if user_id not in user_messages:
            user_messages[user_id] = [SYSTEM_PROMPT]

        components = get_components_from_db(db)
        components_text = "\n".join(
            f"{c.id}: {c.type} {c.name} — {c.price} ₽ ({c.description})" for c in components
        )

        user_messages[user_id].append(
            {"role": "user", "content": f"{user_input}\n\nДоступные комплектующие:\n{components_text}"}
        )

        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=user_messages[user_id]
        )

        response = chat_completion.choices[0].message.content
        user_messages[user_id].append({"role": "assistant", "content": response})

        parsed_response = json.loads(response)
        return FinalAnswer(**parsed_response)

    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI:")
        return FinalAnswer(
            thoughts=[],
            choosen_complect=[],
            final_answer="❌ Произошла ошибка при обработке запроса к ИИ.",
        )


def handle_ai_request(prompt: str, user_id: int, db: Session) -> FinalAnswer:
    return chat_with_gpt(prompt, user_id, db)
