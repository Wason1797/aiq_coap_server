from typing import Optional, Tuple

import aiocoap  # type: ignore
import aiocoap.numbers.constants as constants  # type: ignore
from aiocoap.numbers.constants import TransportTuning  # type: ignore


def configure_transport_tuning(empty_ack_delay: float) -> None:
    """Configure aiocoap transport tuning parameters for CoAP messages.

    aiocoap decodes incoming UDP datagrams without explicit transport_tuning parameters,
    defaulting each incoming request to TransportTuning(). Setting empty_ack_delay
    here ensures incoming confirmable requests buffer sufficient time for resource
    handlers to complete, preventing premature empty ACKs and guaranteeing piggybacked ACKs.
    """
    TransportTuning.EMPTY_ACK_DELAY = empty_ack_delay
    constants._default_transport_tuning.EMPTY_ACK_DELAY = empty_ack_delay


async def create_coap_server_context(
    empty_ack_delay: float,
    bind_ip: Optional[str] = None,
    is_dev: bool = False,
) -> aiocoap.Context:
    """Initialize the aiocoap server context with custom transport tuning and bind settings."""
    configure_transport_tuning(empty_ack_delay)
    binds: Optional[Tuple[str, Optional[int]]] = (
        (bind_ip, None) if bind_ip else (("localhost", None) if is_dev else None)
    )
    return await aiocoap.Context.create_server_context(None, bind=binds)
