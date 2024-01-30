import traceback
from typing import Awaitable, Callable, Iterable, Optional
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from app.config.env_manager import StationType


class ManagementBot:
    dispatcher = Dispatcher()
    _bot: Optional[Bot] = None
    _allow_list: Optional[tuple] = None
    _notification_user: Optional[int] = None
    _commands: dict[str, Callable[[], Awaitable[str]]] = dict()
    _station_type: Optional[StationType] = None
    _location_id: Optional[str] = None

    @classmethod
    def init_bot(cls, token: str, allow_list: Iterable, admin_user: int, station_type: StationType, location_id: str):
        cls._bot = Bot(token, parse_mode=ParseMode.HTML)
        cls._allow_list = tuple(allow_list)
        cls._notification_user = admin_user
        cls._station_type = station_type
        cls._location_id = location_id

    @classmethod
    async def start_polling(cls) -> None:
        return await cls.dispatcher.start_polling(cls.bot())

    @classmethod
    async def stop_polling(cls) -> None:
        return await cls.dispatcher.stop_polling()

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

    @classmethod
    def is_requested_location(cls, requested_location: Optional[str]) -> bool:
        if not requested_location:
            return False
        return cls._location_id == requested_location

    @classmethod
    def is_main_server(cls) -> bool:
        return cls._station_type == StationType.MAIN_SERVER


@ManagementBot.dispatcher.message(CommandStart())
async def command_start_handler(message: Message):
    if not ManagementBot.is_main_server():
        return

    if message.from_user:
        await message.answer(f"Hello {message.from_user.id}")


@ManagementBot.dispatcher.message(Command("summary"))
async def command_summary_handler(message: Message, command: CommandObject):
    if not ManagementBot.is_requested_location(command.args):
        return

    if not ManagementBot.has_command(command.command):
        await message.answer("Command not supported")

    if message.from_user and message.from_user.id not in ManagementBot.get_allow_list():
        await message.answer("User not allowed")
        return

    callback = ManagementBot.get_command(command.command)
    try:
        result = await callback()
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in summary:\n {trace}")
        return

    await message.answer(result)


@ManagementBot.dispatcher.message(Command("truncate"))
async def command_truncate_db_handler(message: Message, command: CommandObject):
    if ManagementBot.is_main_server():
        return

    if not ManagementBot.is_requested_location(command.args):
        return

    if message.from_user and message.from_user.id not in ManagementBot.get_allow_list():
        await message.answer("User not allowed")
        return

    if not ManagementBot.has_command(command.command):
        await message.answer("Command not supported")

    callback = ManagementBot.get_command(command.command)
    try:
        result = await callback()
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in truncate:\n {trace}")
        return

    await message.answer(result)
