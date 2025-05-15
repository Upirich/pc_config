from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from openai import OpenAI

DATABASE_URL = "sqlite:///./pc_components_100.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Component(Base):
    __tablename__ = "components"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)


class Complect(BaseModel):
    id: int
    type: str
    name: str
    price: int
    description: str


class Think(BaseModel):
    explanation: str
    output: str


class FinalAnswer(BaseModel):
    thoughts: List[Think]
    choosen_complect: List[Complect]
    final_answer: str


client = OpenAI(
    api_key="sk-KZBayWeUNOHz0lGu1xOEVxVizGudZ5JF",
    base_url="https://api.proxyapi.ru/openai/v1",
)


def get_complects_from_db():
    db = SessionLocal()
    comps = db.query(Component).all()
    db.close()
    return [
        Complect(
            id=c.id, type=c.type, name=c.name, price=c.price, description=c.description
        )
        for c in comps
    ]


def make_complects_string(complects: List[Complect]) -> str:
    lines = []
    for c in complects:
        line = f"{c.id}) {c.type}: {c.name}, {c.price} руб, {c.description}"
        lines.append(line)
    return "\n".join(lines)


def chat_loop():
    complects = get_complects_from_db()
    if not complects:
        print("Комплектующие в базе не найдены")
        return
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

    print(
        "Введи свой запрос (например: 'Собери игровой компьютер с бюджетом 150000 рублей') или 'exit' для выхода:"
    )
    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            print("Выход...")
            break

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

        print("\nМысли модели:")
        for think in answer.thoughts:
            print(f"- {think.explanation} -> {think.output}")

        print("\nВыбранные комплектующие:")
        for c in answer.choosen_complect:
            print(f"{c.type} {c.name} за {c.price} руб")

        print("\nИтоговый ответ:")
        print(answer.final_answer)
        print("\n---\n")


if __name__ == "__main__":
    chat_loop()
