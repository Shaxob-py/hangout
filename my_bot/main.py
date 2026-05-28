import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from my_bot.keyboard import phone_number
from database import User
from root.config import settings

dp = Dispatcher()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Salom Raqamingizni kriting", reply_markup=phone_number())


@dp.message(F.contact)
async def command_contact_handler(message: Message) -> None:

    if message.from_user.id != message.contact.user_id:
        await message.answer('Ozingizni raqamingizni kriting ❗️️')
        return

    user = await User.get_by_phone(message.contact.phone_number)

    if user is None:
        await User.create(phone=message.contact.phone_number,
                          username=message.from_user.username or message.from_user.first_name,
                          telegram_id=message.from_user.id)

        await message.answer("Royxattan muvaffaqiyatli o'tdingiz ✅")

    await message.answer("login qilishingiz mumkun  ✅")


# Run the bot
# async def main() -> None:
#     bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
#
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
