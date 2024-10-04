import aiocoap.resource as resource  # type: ignore
from aiocoap import CONTENT, Message
from app.log import log


class IndexResource(resource.Resource):
    def __init__(self, version: str):
        self.version = version
        super().__init__()

    async def render_get(self, request) -> Message:
        response = f"AIQ COAP SERVER v-{self.version}"
        log.info(f"index: {response}")
        return Message(code=CONTENT, payload=response.encode("ascii"))
