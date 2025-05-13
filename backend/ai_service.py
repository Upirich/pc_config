import requests

API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"


def is_pc_related(prompt: str) -> bool:
    keywords = [
        "пк",
        "сборка",
        "комплектующие",
        "видеокарта",
        "процессор",
        "собери",
        "игровой",
        "офисный",
        "железо",
        "апгрейд",
        "ssd",
        "hdd",
        "материнская плата",
        "оперативка",
        "блок питания",
        "бюджет",
    ]
    prompt_lower = prompt.lower()
    return any(word in prompt_lower for word in keywords)


def ask_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "PC Config Assistant",
    }
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return "❌ Ошибка при обращении к ИИ."


def handle_ai_request(prompt: str) -> str:
    if is_pc_related(prompt):
        return ask_openrouter(prompt)
    else:
        return "💡 Я помогаю только с выбором комплектующих и сборкой ПК. Попробуйте сформулировать вопрос иначе."
