from aiocoap import Message, CHANGED
import aiocoap.resource as resource

from app.repositories.postgres.managers import AiqDataManager
from app.repositories.postgres.database import PostgresqlConnector


class AiqDataResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_put(self, request) -> Message:
        message = request.payload.decode("ascii")
        session = PostgresqlConnector.get_session()
        await AiqDataManager.save_sensor_data(session, message)
        return Message(code=CHANGED, payload="")
