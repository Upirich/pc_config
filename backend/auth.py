from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
import logging

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Пытаемся использовать bcrypt, если доступен
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    logger.info("BCrypt backend успешно загружен")
except Exception as e:
    logger.warning(f"Ошибка загрузки BCrypt: {e}, используем pbkdf2_sha256 как fallback")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля и его хеша"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Ошибка верификации пароля: {e}")
        return False

def get_password_hash(password: str) -> str:
    """Генерирует хеш пароля"""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Ошибка хеширования пароля: {e}")
        raise

async def authenticate_user(
    session: AsyncSession, 
    email: str, 
    password: str
):
    """Аутентифицирует пользователя по email и паролю"""
    try:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None
            
        if not verify_password(password, user.hashed_password):
            return None

        return user
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {e}")
        return None