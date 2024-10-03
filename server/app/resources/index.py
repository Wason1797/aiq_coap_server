import aiocoap.resource as resource  # type: ignore
from aiocoap import CONTENT, Message


class IndexResource(resource.Resource):
    def __init__(self, version: str):
        self.version = version
        super().__init__()

    async def render_get(self, request) -> Message:
        return Message(code=CONTENT, payload=f"AIQ COAP SERVER v{self.version}".encode("ascii"))
