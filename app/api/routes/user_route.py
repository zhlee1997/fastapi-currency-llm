from fastapi import APIRouter, HTTPException
from aiogram.types.message import Message

from app.api.models import TelegramMessageRequest
from app.dependencies import TelegramBotDep

router = APIRouter()


@router.post("/send-message")
async def send_message_to_current_user(
    message_request: TelegramMessageRequest,
    # current_user: CurrentUserDep,
    telegram_bot: TelegramBotDep,
) -> Message:
    result = await telegram_bot.send_message(-4620023931, message_request.message)
    return result
