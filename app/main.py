import os
import requests

from fastapi import FastAPI, BackgroundTasks
from dotenv import load_dotenv
from openai import OpenAI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from contextlib import asynccontextmanager

from app.api.routes.trip_route import router as trip_route
from app.api.routes.user_route import router as user_route
from app.dependencies import TelegramBotDep, get_telegram_bot
from app.config import settings

import asyncio
from aiogram import Bot


load_dotenv()
CURRENCY_API_TOKEN = os.getenv("CURRENCY_API_TOKEN")
OPENROUTER_API_TOKEN = os.getenv("OPENROUTER_API_TOKEN")


scheduler = AsyncIOScheduler(timezone=utc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting APScheduler...")
    scheduler.start()

    # ✅ Register the scheduled job after scheduler starts
    scheduler.add_job(scheduled_task, "interval", hours=8)

    yield
    print("Shutting down APScheduler...")
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_TOKEN,
)

all_todos = [{"todo_id": 1, "todo_name": "Sports"}]

app.include_router(trip_route, prefix="/api/v1")
app.include_router(user_route, prefix="/api/v1")


@app.get("/")
def index():
    return "Bot is running"


@app.get("/todos")
def todos():
    return all_todos


def get_latest_currency():
    url = "https://api.currencyapi.com/v3/latest?base_currency=SGD"
    headers = {"apikey": CURRENCY_API_TOKEN}
    response = requests.request("GET", url, headers=headers)
    res = response.json()

    return res["data"]["MYR"]


async def send_telegram_message(telegram_bot: TelegramBotDep, message: str):
    """Function to send a message to the Telegram group."""
    await telegram_bot.send_message(settings.TELEGRAM_CHAT_ID, message)


@app.get("/query-model")
def query_model(
    background_tasks: BackgroundTasks,
    telegram_bot: TelegramBotDep,
) -> dict:
    try:
        messages = [
            {
                "role": "user",
                "content": "What is the latest conversion rate for 1 SGD to MYR? And please answer in a smooth and natural way.",
            }
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_latest_currency",
                    "description": "Get the latest conversion rate for 1 SGD to MYR",
                },
            }
        ]

        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=messages,
            tools=tools,
        )

        tool_call = completion.choices[0].message.tool_calls[0]
        # args = json.loads(tool_call.function.arguments)
        result = get_latest_currency()

        messages.append(
            completion.choices[0].message
        )  # append model's function call message
        messages.append(
            {  # append result message
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result),
            }
        )

        completion_2 = client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-preview-02-05:free",
            messages=messages,
            tools=tools,
        )

        response_data = {
            "ok": True,
            "result": completion_2.choices[0].message.content,
            "tool_call_id": tool_call.id,
        }

        # Send Telegram message in the background after returning success response
        message_content = f"Model Response: {response_data['result']}"
        background_tasks.add_task(send_telegram_message, telegram_bot, message_content)

        # return success response
        return response_data
    except Exception as e:
        # return error response
        return {
            "ok": False,
            "error": str(e),
        }


async def scheduled_task():
    """Wrapper function to call `query_model` without arguments."""
    try:
        from fastapi import BackgroundTasks

        background_tasks = BackgroundTasks()
        telegram_bot = get_telegram_bot()  # Manually get the dependency
        result = query_model(background_tasks, telegram_bot)

        print("Scheduled task executed: ", result)
        if result["ok"]:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            message_content = f"Scheduled Model Response: {result['result']}"

            # ✅ Use async with to ensure the session is properly closed
            async with Bot(token=settings.TELEGRAM_BOT_TOKEN) as bot:
                await bot.send_message(settings.TELEGRAM_CHAT_ID, message_content)
        else:
            raise Exception(result["error"])

    except Exception as e:
        print("Error in scheduled task:", str(e))
