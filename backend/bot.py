from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import select
from database import AsyncSessionLocal
from auth import authenticate_user
from models import User, AIChatHistory
import config


bot = Bot(token='7127595559:AAFCh9LzAiNJmehxIezib9NJFfiQnWUJIzA')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class AuthStates(StatesGroup):
    email = State()
    password = State()

auth_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔑 Войти")]],
    resize_keyboard=True
)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📜 История запросов")],
        [KeyboardButton(text="🚪 Выйти")],
    ],
    resize_keyboard=True
)

# Добавляем глобальное хранилище для данных пользователя
user_data_store = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Для доступа к истории войдите в аккаунт.",
        reply_markup=auth_keyboard
    )

@dp.message(F.text == "🔑 Войти")
async def cmd_login(message: types.Message, state: FSMContext):
    await state.set_state(AuthStates.email)
    await message.answer(
        "Введите ваш email:",
        reply_markup=types.ReplyKeyboardRemove()
    )

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
                    reply_markup=auth_keyboard
                )
                await state.clear()
                return
                
            await state.update_data(email=email)
            await state.set_state(AuthStates.password)
            await message.answer("Введите ваш пароль:")
            
    except Exception as e:
        print(f"Ошибка проверки email: {e}")
        await message.answer(
            "⚠️ Произошла ошибка. Попробуйте позже.",
            reply_markup=auth_keyboard
        )
        await state.clear()

@dp.message(AuthStates.password)
async def process_password(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        email = user_data['email']
        password = message.text
        
        async with AsyncSessionLocal() as session:
            user = await authenticate_user(session, email, password)
            
            if not user:
                await message.answer(
                    "❌ Неверный пароль. Нажмите '🔑 Войти' чтобы попробовать снова",
                    reply_markup=auth_keyboard
                )
                await state.clear()
                return
                
            # Сохраняем user_id в глобальное хранилище
            user_data_store[message.from_user.id] = {"user_id": user.id}
            
            await message.answer(
                "✅ Вы успешно авторизованы!",
                reply_markup=main_keyboard
            )
            await state.clear()
            
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        await message.answer(
            "⚠️ Произошла ошибка. Попробуйте позже.",
            reply_markup=auth_keyboard
        )
        await state.clear()

@dp.message(F.text == "📜 История запросов")
async def cmd_history(message: types.Message):
    # Проверяем авторизацию через глобальное хранилище
    if message.from_user.id not in user_data_store:
        await message.answer(
            "❌ Сначала авторизуйтесь",
            reply_markup=auth_keyboard
        )
        return
    
    user_id = user_data_store[message.from_user.id]["user_id"]
    
    try:
        async with AsyncSessionLocal() as session:
            history = await session.execute(
                select(AIChatHistory)
                .where(AIChatHistory.user_id == user_id)
                .order_by(AIChatHistory.timestamp.desc())
                .limit(10)
            )
            history_items = history.scalars().all()
        
        if not history_items:
            await message.answer(
                "📭 История запросов пуста",
                reply_markup=main_keyboard
            )
            return
        
        response = ["📚 Ваша история запросов:\n"]
        for item in history_items:
            response.append(
                f"🕒 {item.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
                f"❓ Вопрос: {item.prompt[:100]}...\n"
                f"💡 Ответ: {item.response[:100]}...\n"
                f"────────────────────"
            )
        
        await message.answer("\n".join(response))
        
    except Exception as e:
        print(f"Ошибка получения истории: {e}")
        await message.answer(
            "⚠️ Не удалось загрузить историю",
            reply_markup=main_keyboard
        )

@dp.message(F.text == "🚪 Выйти")
async def cmd_logout(message: types.Message):
    # Удаляем данные пользователя из хранилища
    if message.from_user.id in user_data_store:
        del user_data_store[message.from_user.id]
    
    await message.answer(
        "Вы вышли из аккаунта. Чтобы продолжить, авторизуйтесь снова.",
        reply_markup=auth_keyboard
    )