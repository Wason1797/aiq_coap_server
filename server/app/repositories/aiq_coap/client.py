from aiocoap import Context, Message, PUT, GET, DELETE  # type: ignore

from typing import Optional


class CoapClient:
    class Response:
        def __init__(self, code: int, payload: str) -> None:
            self.code = code
            self.payload = payload

    @classmethod
    def get_instance(cls, server_uri: Optional[str]) -> Optional["CoapClient"]:
        if not server_uri:
            return None

        return cls(server_uri)

    def __init__(self, server_uri: str) -> None:
        self.server_uri = server_uri
        self.context = None

    async def __aenter__(self):
        self.context = await Context.create_client_context()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.context.shutdown()
        self.context = None

    async def put_payload(self, payload: str) -> Response:
        if self.context is None:
            raise Exception("Cannot put payload before initialization")
        request = Message(code=PUT, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)

    async def get_payload(self, payload: str) -> Response:
        if self.context is None:
            raise Exception("Cannot get payload before initialization")
        request = Message(code=GET, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)

    async def delete_payload(self, payload: str) -> Response:
        if self.context is None:
            raise Exception("Cannot delete payload before initialization")
        request = Message(code=DELETE, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)
