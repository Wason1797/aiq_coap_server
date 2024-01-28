from aiocoap import Context, Message, PUT  # type: ignore

from typing import Optional


class CoapClient:
    class Response:
        def __init__(self, code: int, payload: str) -> None:
            self.code = code
            self.payload = payload

    @classmethod
    async def get_instance(cls, server_uri: Optional[str]) -> Optional["CoapClient"]:
        if not server_uri:
            return None

        context = await Context.create_client_context()
        return cls(server_uri, context)

    def __init__(self, server_uri: str, context: Context) -> None:
        self.server_uri = server_uri
        self.context = context

    async def put_payload(self, payload: str) -> Response:
        if self.context is None:
            raise Exception("Cannot put payload before initialization")
        request = Message(code=PUT, payload=payload.encode(encoding="ascii"), uri=self.server_uri)

        response = await self.context.request(request).response
        return self.Response(response.code, response.payload)
