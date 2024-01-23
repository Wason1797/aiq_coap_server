from typing import Any, Coroutine
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.config.env_manager import get_settings

EnvManager = get_settings()
ALLOW_LIST = tuple(EnvManager.get_allowed_users())


class ManagementBot:
    _bot = Bot(EnvManager.BOT_TOKEN, parse_mode=ParseMode.HTML)
    _dispatcher = Dispatcher()
    _commands: dict[str, Coroutine[str, Any, None]] = dict()

    @classmethod
    async def start_polling(cls) -> None:
        return await cls._dispatcher.start_polling(cls._bot)

    @classmethod
    def bot(cls) -> Bot:
        return cls._bot

    @classmethod
    def has_command(cls, key: str) -> bool:
        return key in cls._commands

    @classmethod
    def get_command(cls, key: str) -> Coroutine[str, Any, None]:
        return cls._commands[key]

    @classmethod
    def register_commad(cls, key: str, callback: Coroutine[str, Any, None]) -> None:
        cls._commands[key] = callback


@ManagementBot._dispatcher.message(CommandStart())
async def command_start_handler(message: Message):
    if message.from_user:
        await message.answer(f"Hello {message.from_user.id}")


@ManagementBot._dispatcher.message(Command("summary"))
async def command_summary_handler(message: Message):
    if not ManagementBot.has_command("summary"):
        await message.answer("Command not supported")

    if message.from_user and message.from_user.id not in ALLOW_LIST:
        await message.answer("User not allowed")
        return

    callback = ManagementBot.get_command("summary")
    result = await callback()
    await message.answer(result)
