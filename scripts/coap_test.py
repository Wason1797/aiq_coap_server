import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)


async def main():
    """Perform a single PUT request to localhost on the default port, URI
    "/other/block". The request is sent 2 seconds after initialization.

    The payload is bigger than 1kB, and thus sent as several blocks."""

    context = await Context.create_client_context()

    await asyncio.sleep(2)

    payload = b"1"
    request = Message(code=GET, payload=payload, uri="coap://localhost/index")

    response = await context.request(request).response

    print("Result: %s\n%r" % (response.code, response.payload))


if __name__ == "__main__":
    asyncio.run(main())
