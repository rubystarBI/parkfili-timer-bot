import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("BOT_TOKEN")  # Укажите ваш токен в переменной окружения

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

target_datetime = None
countdown_message_id = None
countdown_chat_id = None
countdown_task = None

def format_time_delta(delta: timedelta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"

async def start_countdown():
    global countdown_message_id, countdown_chat_id, target_datetime

    while True:
        now = datetime.now()
        if target_datetime <= now:
            await bot.edit_message_text(
                "🎉 ЭКОАКЦИЯ В ПАРКЕ ФИЛИ НАЧАЛАСЬ!",
                chat_id=countdown_chat_id,
                message_id=countdown_message_id
            )
            break

        time_left = target_datetime - now
        formatted = format_time_delta(time_left)
        text = f"🌿 ДО ЭКОАКЦИИ В ПАРКЕ ФИЛИ осталось {formatted}"

        try:
            await bot.edit_message_text(
                text,
                chat_id=countdown_chat_id,
                message_id=countdown_message_id
            )
        except Exception as e:
            print("Ошибка при обновлении сообщения:", e)

        await asyncio.sleep(1)

@dp.message_handler(commands=['setdate'])
async def set_date(message: Message):
    global target_datetime, countdown_message_id, countdown_chat_id, countdown_task

    try:
        args = message.get_args()
        target_datetime = datetime.strptime(args, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        if target_datetime <= now:
            await message.reply("Укажите дату и время **в будущем**. Формат: `/setdate 2025-04-25 15:00:00`", parse_mode="Markdown")
            return

        countdown_chat_id = message.chat.id

        # Отправляем первое сообщение
        time_left = target_datetime - now
        formatted = format_time_delta(time_left)
        countdown_message = await message.reply(f"🌿 ДО ЭКОАКЦИИ В ПАРКЕ ФИЛИ осталось {formatted}")
        countdown_message_id = countdown_message.message_id

        # Останавливаем старую задачу, если есть
        if countdown_task:
            countdown_task.cancel()

        countdown_task = asyncio.create_task(start_countdown())

    except ValueError:
        await message.reply("Неверный формат даты. Используйте: `/setdate 2025-04-25 15:00:00`", parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp)
