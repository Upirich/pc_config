from openai import OpenAI

client = OpenAI(
    api_key="sk-KZBayWeUNOHz0lGu1xOEVxVizGudZ5JF",
    base_url="https://api.proxyapi.ru/openai/v1",
)

messages = [
    {"role": "system", "content": "Ты ассистент, который помогает только с вопросами по компьютерам, сборке ПК и выбору комплектующих. Пожалуйста, отвечай только на эти вопросы."}
]

def chat_with_gpt(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    chat_completion = client.chat.completions.create(model="gpt-4o", messages=messages)

    response = chat_completion.choices[0].message.content
    messages.append({"role": "assistant", "content": response})

    return response

def handle_ai_request(prompt: str) -> str:
    return chat_with_gpt(prompt)

while True:
    user_input = input("Вы: ")
    if user_input.lower() in ["выход", "exit"]:
        break
    response = handle_ai_request(user_input)
    print("AI: " + response)
