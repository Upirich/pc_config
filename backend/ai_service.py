from openai import OpenAI
from typing import Dict, List
import logging
from sqlalchemy.orm import Session
from fastapi import Depends
from db1 import get_db1
from models import Component
from schemas import Complect, Think, FinalAnswer

client = OpenAI(
    api_key="sk-KZBayWeUNOHz0lGu1xOEVxVizGudZ5JF",
    base_url="https://api.proxyapi.ru/openai/v1",
)


def get_complects_from_db(db: Session) -> List[Complect]:
    comps = db.query(Component).all()
    return [
        Complect(
            id=c.id,
            type=c.type,
            name=c.name,
            price=c.price,
            description=c.description,
        )
        for c in comps
    ]


def make_complects_string(complects: List[Complect]) -> str:
    lines = []
    for c in complects:
        line = f"{c.id}) {c.type}: {c.name}, {c.price} руб, {c.description}"
        lines.append(line)
    return "\n".join(lines)


def handle_cot_ai_request(user_input: str, db: Session) -> FinalAnswer:
    complects = get_complects_from_db(db)
    if not complects:
        raise ValueError("Комплектующие в базе не найдены")

    compl_string = make_complects_string(complects)

    system_prompt = (
        "Ты ассистент по сборке ПК.\n"
        "ВНИМАНИЕ! Вот доступные комплектующие для сборки:\n"
        f"{compl_string}\n"
        "Используй ТОЛЬКО эти компоненты для сборки ПК по запросу пользователя.\n"
        "Сделай Chain of Thought:\n"
        "1) Подробно объясни выбор каждого компонента, почему он лучший для данного запроса и бюджета.\n"
        "2) Укажи, какие преимущества этот компонент даёт в игровом ПК.\n"
        "3) Перечисли выбранные компоненты с их характеристиками.\n"
        "4) В конце дай итоговый, развернутый ответ с рекомендациями и общим обзором сборки.\n"
        "Отвечай подробно и аргументированно, учитывая цену и характеристики каждого компонента."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=messages,
        text_format=FinalAnswer,
    )
    answer: FinalAnswer = response.output_parsed
    return answer


def handle_ai_cot_request(prompt: str, db: Session) -> FinalAnswer:
    try:
        return handle_cot_ai_request(prompt, db)
    except Exception as e:
        logging.exception("Ошибка при обработке Chain of Thought ИИ запроса:")
        raise e


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
            model="gpt-4o", messages=user_messages[user_id]
        )

        response = chat_completion.choices[0].message.content
        user_messages[user_id].append({"role": "assistant", "content": response})
        return response

    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI:")
        return "❌ Произошла ошибка при обработке запроса к ИИ."


def handle_ai_request(prompt: str, user_id: int) -> str:
    return chat_with_gpt(prompt, user_id)
