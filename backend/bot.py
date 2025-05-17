from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from typing import Union
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import select
from database import AsyncSessionLocal
from auth_tg import authenticate_user
from models import User, AIRequestChat
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InputFile, BufferedInputFile
import requests


class YandexSpeechKit:
    def __init__(self, api_key, folder_id):
        self.api_key = api_key
        self.folder_id = folder_id
        self.url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

    def synthesize(self, text, voice="alena", format="oggopus"):
        headers = {"Authorization": f"Api-Key {self.api_key}"}
        data = {
            "text": text,
            "voice": voice,
            "folderId": self.folder_id,
            "format": format,
        }
        response = requests.post(self.url, headers=headers, data=data)
        return response.content if response.status_code == 200 else None


# SPEECHKIT_API_KEY = "AQVN1-bH8__4Zl61UV8cCMquwlivOcF9rveueJBe"
# FOLDER_ID = "b1g4nqubucfntfi07tr9"  # Если используется
VOICE = "alena"  # Голос Алисы

speechkit = YandexSpeechKit(
    api_key="AQVN1-bH8__4Zl61UV8cCMquwlivOcF9rveueJBe", folder_id="b1g4nqubucfntfi07tr9"
)


async def text_to_speech(text: str, chat_id: int) -> str:
    """Преобразует текст в аудио и возвращает путь к файлу"""
    try:
        audio = speechkit.synthesize(text=text, voice=VOICE, format="oggopus")
        filename = f"voice_{chat_id}.ogg"
        with open(filename, "wb") as f:
            f.write(audio)
        return filename
    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")
        return None


bot = Bot(token="7127595559:AAFCh9LzAiNJmehxIezib9NJFfiQnWUJIzA")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class AuthStates(StatesGroup):
    email = State()
    password = State()


auth_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔑 Войти")]], resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 История запросов")],
        [KeyboardButton(text="🚪 Выйти")],
    ],
    resize_keyboard=True,
)

# Добавляем глобальное хранилище для данных пользователя
user_data_store = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Для доступа к истории войдите в аккаунт.",
        reply_markup=auth_keyboard,
    )


@dp.message(F.text == "🔑 Войти")
async def cmd_login(message: types.Message, state: FSMContext):
    await state.set_state(AuthStates.email)
    await message.answer("Введите ваш email:", reply_markup=types.ReplyKeyboardRemove())


@dp.message(AuthStates.email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == email))
            user_exists = result.scalar_one_or_none() is not None

            if not user_exists:
                await message.answer(
                    "❌ Пользователь с таким email не найден. Нажмите '🔑 Войти' чтобы попробовать снова",
                    reply_markup=auth_keyboard,
                )
                await state.clear()
                return

            await state.update_data(email=email)
            await state.set_state(AuthStates.password)
            await message.answer("Введите ваш пароль:")

    except Exception as e:
        print(f"Ошибка проверки email: {e}")
        await message.answer(
            "⚠️ Произошла ошибка. Попробуйте позже.", reply_markup=auth_keyboard
        )
        await state.clear()


@dp.message(AuthStates.password)
async def process_password(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        email = user_data["email"]
        password = message.text

        async with AsyncSessionLocal() as session:
            user = await authenticate_user(session, email, password)

            if not user:
                await message.answer(
                    "❌ Неверный пароль. Попробуйте снова", reply_markup=auth_keyboard
                )
                await state.clear()
                return

            # Сохраняем user_id в глобальное хранилище
            user_data_store[message.from_user.id] = {"user_id": user.id}

            await message.answer(
                "✅ Вы успешно авторизованы!", reply_markup=main_keyboard
            )
            await state.clear()

    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        await message.answer(
            "⚠️ Произошла ошибка. Попробуйте позже.", reply_markup=auth_keyboard
        )
        await state.clear()


@dp.message(F.text == "📜 История запросов")
async def cmd_history(message: types.Message):
    if message.from_user.id not in user_data_store:
        await message.answer("❌ Сначала авторизуйтесь", reply_markup=auth_keyboard)
        return

    user_id = user_data_store[message.from_user.id]["user_id"]

    try:
        async with AsyncSessionLocal() as session:
            history = await session.execute(
                select(AIRequestChat)
                .where(AIRequestChat.user_id == user_id)
                .order_by(AIRequestChat.created_at.desc())
                .limit(10)
            )
            history_items = history.scalars().all()

        if not history_items:
            await message.answer(
                "📭 История запросов пуста", reply_markup=main_keyboard
            )
            return

        response = ["📚 Последние 10 запросов:\n"]
        for item in history_items:
            response.append(
                f"🕒 {item.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"❓ Вопрос: {item.request_text[:100]}{'...' if len(item.request_text) > 100 else ''}\n"
                f"💡 Ответ: {item.response_text[:100]}{'...' if len(item.response_text) > 100 else ''}\n"
                f"────────────────────"
            )

        # Добавляем кнопку "Прослушать"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔊 Прослушать последний ответ", callback_data="play_last"
                    )
                ]
            ]
        )

        await message.answer("\n".join(response), reply_markup=keyboard)

    except Exception as e:
        print(f"Ошибка получения истории: {e}")
        await message.answer(
            "⚠️ Не удалось загрузить историю", reply_markup=main_keyboard
        )


# Обработчик кнопки "Прослушать"
@dp.callback_query(F.data == "play_last")
async def play_last_answer(callback: types.CallbackQuery):
    try:
        if callback.from_user.id not in user_data_store:
            await callback.answer("❌ Требуется авторизация", show_alert=True)
            return

        user_id = user_data_store[callback.from_user.id]["user_id"]

        async with AsyncSessionLocal() as session:
            history = await session.execute(
                select(AIRequestChat)
                .where(AIRequestChat.user_id == user_id)
                .order_by(AIRequestChat.created_at.desc())
                .limit(10)  # Ограничиваем количество для озвучки
            )
            history_items = history.scalars().all()

            if not history_items:
                await callback.answer("❌ Нет истории для озвучки", show_alert=True)
                return

            # Формируем полный текст для озвучки
            full_text = "Ваша история запросов:\n\n"
            for i, item in enumerate(
                reversed(history_items), 1
            ):  # Обратный порядок для хронологии
                full_text += (
                    f"Запрос {i} от {item.created_at.strftime('%d.%m.%Y %H:%M')}:\n"
                    f"Вопрос: {item.request_text}\n"
                    f"Ответ: {item.response_text}\n\n"
                )

            # Ограничиваем длину текста (максимум 5000 символов для SpeechKit)
            full_text = full_text[:5000]

            # Синтезируем речь
            audio_data = await text_to_speech_bytes(full_text)

            if audio_data:
                voice_message = BufferedInputFile(
                    file=audio_data, filename="history.ogg"
                )
                await callback.message.answer_voice(
                    voice=voice_message, caption="История ваших запросов"
                )
            else:
                await callback.answer("⚠️ Ошибка синтеза речи", show_alert=True)

    except Exception as e:
        print(f"Ошибка озвучки истории: {e}")
        await callback.answer("⚠️ Произошла ошибка", show_alert=True)


async def text_to_speech_bytes(text: str) -> Union[bytes, None]:
    try:
        audio = speechkit.synthesize(text=text, voice="alena", format="oggopus")
        return audio
    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")
        return None


@dp.message(F.text == "🚪 Выйти")
async def cmd_logout(message: types.Message):
    # Удаляем данные пользователя из хранилища
    if message.from_user.id in user_data_store:
        del user_data_store[message.from_user.id]

    await message.answer(
        "Вы вышли из аккаунта. Чтобы продолжить, авторизуйтесь снова.",
        reply_markup=auth_keyboard,
    )
