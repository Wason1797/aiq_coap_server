from typing import Awaitable, Callable, Iterable, Optional
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message


class ManagementBot:
    _bot: Optional[Bot] = None
    _allow_list: Optional[tuple] = None
    _notification_user: Optional[int] = None
    _dispatcher = Dispatcher()
    _commands: dict[str, Callable[[], Awaitable[str]]] = dict()

    @classmethod
    def init_bot(cls, token: str, allow_list: Iterable, admin_user: int):
        cls._bot = Bot(token, parse_mode=ParseMode.HTML)
        cls._allow_list = tuple(allow_list)
        cls._notification_user = admin_user

    @classmethod
    async def start_polling(cls) -> None:
        return await cls._dispatcher.start_polling(cls.bot())

    @classmethod
    def bot(cls) -> Bot:
        if not cls._bot:
            raise Exception("Bot not initialized")
        return cls._bot

    @classmethod
    def has_command(cls, key: str) -> bool:
        return key in cls._commands

    @classmethod
    def get_command(cls, key: str) -> Callable[[], Awaitable[str]]:
        return cls._commands[key]

    @classmethod
    def register_commad(cls, key: str, callback: Callable[[], Awaitable[str]]) -> None:
        cls._commands[key] = callback

    @classmethod
    def get_allow_list(cls) -> tuple:
        return cls._allow_list if cls._allow_list is not None else tuple()

    @classmethod
    async def send_notification(cls, text: str) -> None:
        if cls._notification_user is None:
            print("Admin user not found, cannot send notification")
            return
        await cls.bot().send_message(cls._notification_user, text)


@ManagementBot._dispatcher.message(CommandStart())
async def command_start_handler(message: Message):
    if message.from_user:
        await message.answer(f"Hello {message.from_user.id}")


@ManagementBot._dispatcher.message(Command("summary"))
async def command_summary_handler(message: Message):
    if not ManagementBot.has_command("summary"):
        await message.answer("Command not supported")

    if message.from_user and message.from_user.id not in ManagementBot.get_allow_list():
        await message.answer("User not allowed")
        return

    callback = ManagementBot.get_command("summary")
    result = await callback()
    await message.answer(result)
