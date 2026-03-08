import json

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError


class MessageError(BaseModel):
    pass


class UnknownJsonError(MessageError):
    fields: dict[str, object]


class MalformedMessageError(MessageError):
    original_input: str


class ValidationError(MessageError):
    type_name: str
    fields: dict[str, object]


class MessageSerialize:
    def __init__(self) -> None:
        self._registered_types: set[type] = set()
        self._types_by_name: dict[str, type[BaseModel]] = {}

    def register_type(self, model_type: type[BaseModel]) -> None:
        if not issubclass(model_type, BaseModel):
            raise TypeError(f"{model_type.__name__} must be a pydantic BaseModel")
        self._registered_types.add(model_type)
        self._types_by_name[model_type.__name__] = model_type

    def serialize(self, message: BaseModel) -> bytes:
        if type(message) not in self._registered_types:
            raise ValueError(f"Type {message.__class__.__name__} is not registered")
        payload = message.model_dump()
        payload["$type"] = message.__class__.__name__
        return json.dumps(payload).encode("utf-8")

    def deserialize(self, data: bytes) -> BaseModel:
        try:
            decoded_data = data.decode("utf-8")
            payload = json.loads(decoded_data)
        except UnicodeDecodeError, json.JSONDecodeError:
            return MalformedMessageError(
                original_input=data.decode("utf-8", errors="replace")
            )

        type_name = payload.get("$type")
        model_type = self._types_by_name.get(type_name)
        if model_type is None:
            return UnknownJsonError(fields=payload)

        model_payload = dict(payload)
        model_payload.pop("$type", None)
        try:
            return model_type(**model_payload)
        except PydanticValidationError:
            return ValidationError(type_name=type_name, fields=model_payload)


def create_default_serializer() -> MessageSerialize:
    serializer = MessageSerialize()
    from messaging.villager.events import VillagerCreated

    serializer.register_type(VillagerCreated)
    return serializer
