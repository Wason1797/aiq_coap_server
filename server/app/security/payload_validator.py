import hmac
from typing import NamedTuple, Optional, Type

from pydantic import BaseModel


class ValidatorResult(NamedTuple):
    data: BaseModel
    border_router_id: Optional[int]


class PayloadValidator:
    secret_key: Optional[str] = None

    @classmethod
    def init_validator(cls, secret_key: str) -> None:
        cls.secret_key = secret_key

    @classmethod
    def validate(cls, payload: str, model: Type[BaseModel]) -> ValidatorResult:
        if not cls.secret_key:
            raise RuntimeError("Cannot validate payload before initialization")

        payload_chunks = payload.split("|")
        payload_chunk_count = len(payload_chunks)

        assert payload_chunk_count == 2 or payload_chunk_count == 3, f"Invalid payload of size {payload_chunk_count}"

        if payload_chunk_count == 2:
            payload_chunks.append("")

        message, signature_hex, border_router_id = payload_chunks

        message_hex = hmac.new(cls.secret_key.encode("ascii"), message.encode("ascii"), "sha1").hexdigest()

        if hmac.compare_digest(message_hex, signature_hex):
            return ValidatorResult(model.model_validate_json(message), int(border_router_id) if border_router_id else None)

        raise ValueError("Payload has an invalid signature")
