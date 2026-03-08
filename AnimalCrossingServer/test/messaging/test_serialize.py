import json

import pytest
from pydantic import BaseModel

from messaging.serialize import MessageSerialize


class EmptyModel(BaseModel):
    pass


class AnotherEmptyModel(BaseModel):
    pass


@pytest.mark.parametrize(
    "model, expected_type",
    [(EmptyModel(), "EmptyModel"), (AnotherEmptyModel(), "AnotherEmptyModel")],
)
def test_should_serialize_type_for_empty_model(
    model: BaseModel, expected_type: str
) -> None:
    # given
    message = model
    serializer = MessageSerialize()
    serializer.register_type(EmptyModel)
    serializer.register_type(AnotherEmptyModel)

    # when
    result = serializer.serialize(message)

    # then
    payload = json.loads(result.decode("utf-8"))
    assert payload == {"$type": expected_type}


def test_should_serialize_type_and_fields_for_non_empty_model() -> None:
    # given
    class NonEmptyModel(BaseModel):
        name: str
        count: int

    message = NonEmptyModel(name="Isabelle", count=3)
    serializer = MessageSerialize()
    serializer.register_type(NonEmptyModel)

    # when
    result = serializer.serialize(message)

    # then
    payload = json.loads(result.decode("utf-8"))
    assert payload == {"name": "Isabelle", "count": 3, "$type": "NonEmptyModel"}


def test_should_raise_error_for_non_pydantic_model() -> None:
    # given
    class NotPydantic:
        pass

    serializer = MessageSerialize()

    # when
    with pytest.raises(TypeError):
        serializer.register_type(NotPydantic)


def test_should_raise_error_for_unregistered_type() -> None:
    # given
    class UnregisteredModel(BaseModel):
        value: str

    message = UnregisteredModel(value="test")
    serializer = MessageSerialize()

    # when
    with pytest.raises(ValueError):
        serializer.serialize(message)
