from app.repositories.db.models import BorderRouter
import pytest

from app.managers.br_manager import BorderRouterManager
from app.types import AsyncSessionMaker
from sqlalchemy import select


@pytest.mark.asyncio
async def test_register_border_router_creation(
    main_db_session: AsyncSessionMaker, backup_db_session: AsyncSessionMaker, test_br_data
) -> None:
    result = await BorderRouterManager.register_border_router(
        main_db_session, backup_db_session, test_br_data.ip_v4, test_br_data.location
    )

    assert test_br_data.ip_v4 in result
    assert test_br_data.location in result

    async with main_db_session() as session:
        main_br = (await session.scalars(select(BorderRouter).limit(1))).first()

    async with backup_db_session() as session:
        backup_br = (await session.scalars(select(BorderRouter).limit(1))).first()

    assert main_br and backup_br

    assert main_br.id == backup_br.id
    assert main_br.ipv4_address == backup_br.ipv4_address
    assert main_br.location == backup_br.location


@pytest.mark.asyncio
async def test_register_border_router_update(
    main_db_session: AsyncSessionMaker, backup_db_session: AsyncSessionMaker, test_br_data
) -> None:
    await BorderRouterManager.register_border_router(main_db_session, backup_db_session, test_br_data.ip_v4, test_br_data.location)

    updated_ip = "1.1.1.1"
    updated_location = "updated_location"

    async with main_db_session() as session:
        main_br = (await session.scalars(select(BorderRouter).limit(1))).first()

    result = await BorderRouterManager.register_border_router(
        main_db_session, backup_db_session, updated_ip, updated_location, main_br.id
    )

    assert updated_ip in result
    assert updated_location in result

    async with backup_db_session() as session:
        backup_br = (await session.scalars(select(BorderRouter).limit(1))).first()

    assert backup_br

    assert backup_br.id == main_br.id
    assert updated_ip == backup_br.ipv4_address
    assert updated_location == backup_br.location


@pytest.mark.asyncio
async def test_get_border_router(main_db_session: AsyncSessionMaker, backup_db_session: AsyncSessionMaker, test_br_data) -> None:
    await BorderRouterManager.register_border_router(main_db_session, backup_db_session, test_br_data.ip_v4, test_br_data.location)

    fetched_br = await BorderRouterManager.get_border_router(main_db_session, test_br_data.location)

    assert fetched_br is not None
    assert fetched_br.location == test_br_data.location


@pytest.mark.asyncio
async def test_get_border_router_by_id(main_db_session: AsyncSessionMaker, backup_db_session: AsyncSessionMaker, test_br_data) -> None:
    await BorderRouterManager.register_border_router(main_db_session, backup_db_session, test_br_data.ip_v4, test_br_data.location)

    fetched_br = await BorderRouterManager.get_border_router_by_id(main_db_session, 1)

    assert fetched_br is not None
    assert fetched_br.id == 1
