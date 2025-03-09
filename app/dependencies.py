from typing import Annotated, AsyncGenerator

from fastapi import Depends
from aiogram import Bot

from app.config import settings


async def get_telegram_bot() -> AsyncGenerator[Bot, None]:
    async with Bot(token=settings.TELEGRAM_BOT_TOKEN) as bot:
        yield bot


TelegramBotDep = Annotated[Bot, Depends(get_telegram_bot)]
