import logging
import traceback
from functools import wraps
from typing import Awaitable, Callable, Iterable, Optional, TypeVarTuple

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message

Params = TypeVarTuple("Params")


class ManagementBot:
    dispatcher = Dispatcher()
    _bot: Optional[Bot] = None
    _allow_list: Optional[tuple] = None
    _notification_user: Optional[int] = None
    _commands: dict[str, Callable[[*Params], Awaitable[str]]] = dict()

    @classmethod
    def init_bot(cls, token: str, allow_list: Iterable, admin_user: int):
        cls._bot = Bot(token, parse_mode=ParseMode.HTML)
        cls._allow_list = tuple(allow_list)
        cls._notification_user = admin_user

    @classmethod
    async def start_polling(cls) -> None:
        return await cls.dispatcher.start_polling(cls.bot(), handle_signals=False)

    @classmethod
    async def stop_polling(cls) -> None:
        return await cls.dispatcher.stop_polling()

    @classmethod
    async def close_client_session(cls) -> None:
        return await cls.bot().session.close()

    @classmethod
    def bot(cls) -> Bot:
        if not cls._bot:
            raise Exception("Bot not initialized")
        return cls._bot

    @classmethod
    def has_command(cls, key: str) -> bool:
        return key in cls._commands

    @classmethod
    def get_command(cls, key: str) -> Callable[[*Params], Awaitable[str]]:
        return cls._commands[key]

    @classmethod
    def register_commad(cls, key: str, callback: Callable[[*Params], Awaitable[str]]) -> None:
        cls._commands[key] = callback

    @classmethod
    def get_allow_list(cls) -> tuple:
        return cls._allow_list if cls._allow_list is not None else tuple()

    @classmethod
    async def send_notification(cls, text: str) -> None:
        if cls._notification_user is None:
            logging.info("Admin user not found, cannot send notification")
            return
        await cls.bot().send_message(cls._notification_user, text)

    @classmethod
    def validate_command(cls, fn: Callable) -> Callable:
        @wraps(fn)
        async def wrapper(message: Message, command: CommandObject):
            if message.from_user and message.from_user.id not in cls.get_allow_list():
                await message.answer("User not allowed")
                return

            if not cls.has_command(command.command):
                await message.answer("Command not supported")

            return await fn(message, command)

        return wrapper


@ManagementBot.dispatcher.message(CommandStart())
async def command_start_handler(message: Message):
    if message.from_user:
        await message.answer(f"Hello {message.from_user.id}")


@ManagementBot.dispatcher.message(Command("data_summary"))
@ManagementBot.validate_command
async def command_summary_handler(message: Message, command: CommandObject):
    if not ManagementBot.has_command(command.command):
        await message.answer("Command not supported")

    callback = ManagementBot.get_command(command.command)
    try:
        result = await callback()
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in summary:\n {trace}")
        return

    await message.answer(result)


@ManagementBot.dispatcher.message(Command("station_summary"))
@ManagementBot.validate_command
async def command_summary_station_handler(message: Message, command: CommandObject):
    callback = ManagementBot.get_command(command.command)
    try:
        result = await callback()
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in summary:\n {trace}")
        return

    await message.answer(result)


@ManagementBot.dispatcher.message(Command("register_br"))
@ManagementBot.validate_command
async def command_register_br_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("location and ip_addr needed")
        return

    callback = ManagementBot.get_command(command.command)
    try:
        cmd_args = command.args.split()
        id = None
        if len(cmd_args) == 2:
            location, ip_addr = cmd_args
        elif len(cmd_args) == 3:
            location, ip_addr, id = cmd_args
        else:
            await message.answer(f"Invalid number of arguments, {cmd_args}")
            return
        result = await callback(location, ip_addr, int(id) if id else None)
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in summary:\n {trace}")
        return

    await message.answer(result)


@ManagementBot.dispatcher.message(Command("register_station"))
@ManagementBot.validate_command
async def command_register_station_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("name and Optional[id] needed")
        return

    callback = ManagementBot.get_command(command.command)
    try:
        cmd_args = command.args.split()
        station_id = None
        if len(cmd_args) == 1:
            name = cmd_args[0]
        elif len(cmd_args) == 2:
            name, station_id = cmd_args
        else:
            await message.answer(f"Invalid number of arguments, {cmd_args}")
            return

        result = await callback(name, int(station_id) if station_id else None)
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in summary:\n {trace}")
        return

    await message.answer(result)


@ManagementBot.dispatcher.message(Command("truncate"))
@ManagementBot.validate_command
async def command_truncate_db_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("border_router_id needed")
        return

    callback = ManagementBot.get_command(command.command)
    try:
        result = await callback(command.args)
    except Exception:
        trace = traceback.format_exc()
        await message.answer(f"An error occurred in truncate:\n {trace}")
        return

    await message.answer(result)
