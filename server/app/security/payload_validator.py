import hmac
from typing import Optional, Type

from pydantic import BaseModel


class PayloadValidator:
    secret_key: Optional[str] = None

    @classmethod
    def init_validator(cls, secret_key: str) -> None:
        cls.secret_key = secret_key

    @classmethod
    def validate(cls, payload: str, model: Type[BaseModel]) -> BaseModel:
        if not cls.secret_key:
            raise RuntimeError("Cannot validate payload before initialization")

        message, signature_hex = payload.split("|")
        message_hex = hmac.new(cls.secret_key.encode("ascii"), message.encode("ascii"), "sha1").hexdigest()

        if hmac.compare_digest(message_hex, signature_hex):
            return model.model_validate_json(message)

        raise ValueError("Payload has an invalid signature")
