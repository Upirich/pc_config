from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db
from auth import authenticate_user
from models import AIChatHistory
import config

bot = Bot(token=config.TELEGRAM_TOKEN)
dp = Dispatcher()

# Состояния FSM
class AuthStates(StatesGroup):
    email = State()
    password = State()

# Клавиатуры
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "Добро пожаловать! Для доступа к истории войдите в аккаунт.",
        reply_markup=auth_keyboard
    )

@dp.message(F.text == "🔑 Войти")
async def cmd_login(message: types.Message, state: FSMContext):
    """Начало процесса авторизации"""
    await state.set_state(AuthStates.email)
    await message.answer(
        "Введите ваш email:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(AuthStates.email)
async def process_email(message: types.Message, state: FSMContext):
    """Обработка введенного email"""
    await state.update_data(email=message.text)
    await state.set_state(AuthStates.password)
    await message.answer("Введите ваш пароль:")

@dp.message(AuthStates.password)
async def process_password(message: types.Message, state: FSMContext):
    """Обработка введенного пароля и аутентификация"""
    user_data = await state.get_data()
    email = user_data['email']
    password = message.text
    
    async with get_db() as session:
        user = await authenticate_user(session, email, password)
    
    if not user:
        await message.answer("❌ Неверный email или пароль")
        await state.clear()
        return
    
    await state.update_data(user_id=user.id)
    await message.answer(
        "✅ Вы успешно авторизованы!",
        reply_markup=main_keyboard
    )
    await state.clear()

@dp.message(F.text == "📜 История запросов")
async def cmd_history(message: types.Message):
    """Вывод истории запросов пользователя"""
    async with get_db() as session:
        # В реальном проекте нужно получать user_id из состояния или БД
        # Здесь для примера используем первый найденный аккаунт
        result = await session.execute(select(AIChatHistory).limit(10))
        history = result.scalars().all()
    
    if not history:
        await message.answer("История запросов пуста")
        return
    
    response = ["📚 Ваша история запросов:\n"]
    for item in history:
        response.append(
            f"🕒 {item.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            f"❓ Вопрос: {item.prompt[:100]}...\n"
            f"💡 Ответ: {item.response[:100]}...\n"
            f"────────────────────"
        )
    
    await message.answer("\n".join(response))

@dp.message(F.text == "🚪 Выйти")
async def cmd_logout(message: types.Message):
    """Выход из системы"""
    await message.answer(
        "Вы вышли из системы",
        reply_markup=auth_keyboard
    )