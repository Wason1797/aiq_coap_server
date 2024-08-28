from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable


AsyncSessionMaker = Callable[[], AsyncSession]
