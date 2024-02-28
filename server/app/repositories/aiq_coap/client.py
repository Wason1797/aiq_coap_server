from aiocoap import Context, Message, PUT, GET, DELETE  # type: ignore

from typing import Optional


class CoapClient:
    class Response:
        def __init__(self, code: int, payload: str) -> None:
            self.code = code
            self.payload = payload

    @classmethod
    def get_instance(cls, server_uri: Optional[str], context: Context) -> Optional["CoapClient"]:
        if not server_uri:
            return None

        return cls(server_uri, context)

    def __init__(self, server_uri: str, context: Context) -> None:
        self.server_uri = server_uri
        self.context = context

    async def put_payload(self, payload: str) -> Response:
        request = Message(code=PUT, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)

    async def get_payload(self, payload: str) -> Response:
        request = Message(code=GET, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)

    async def delete_payload(self, payload: str) -> Response:
        request = Message(code=DELETE, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)
