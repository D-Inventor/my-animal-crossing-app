from pydantic import BaseModel

from messaging.serialize import (
    MalformedMessageError,
    MessageSerialize,
    UnknownJsonError,
    ValidationError,
)


def test_should_deserialize_empty_model() -> None:
    # given
    class EmptyModel(BaseModel):
        pass

    data = b'{"$type": "EmptyModel"}'
    serializer = MessageSerialize()
    serializer.register_type(EmptyModel)

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, EmptyModel)


def test_should_deserialize_model_with_fields() -> None:
    # given
    class PersonModel(BaseModel):
        name: str
        age: int

    data = b'{"$type": "PersonModel", "name": "Tom", "age": 30}'
    serializer = MessageSerialize()
    serializer.register_type(PersonModel)

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, PersonModel)
    assert result.name == "Tom"
    assert result.age == 30


def test_should_return_unknown_json_message_for_unregistered_type() -> None:
    # given
    data = b'{"$type": "UnregisteredModel", "name": "Redd", "is_npc": true}'
    serializer = MessageSerialize()

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, UnknownJsonError)
    assert result.fields == {
        "$type": "UnregisteredModel",
        "name": "Redd",
        "is_npc": True,
    }


def test_should_return_unknown_json_message_when_type_is_missing() -> None:
    # given
    data = b'{"name": "Redd", "is_npc": true}'
    serializer = MessageSerialize()

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, UnknownJsonError)
    assert result.fields == {
        "name": "Redd",
        "is_npc": True,
    }


def test_should_return_malformed_message_when_data_is_not_json() -> None:
    # given
    data = b"not-json"
    serializer = MessageSerialize()

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, MalformedMessageError)
    assert result.original_input == "not-json"


def test_should_return_validation_failed_message_for_invalid_fields() -> None:
    # given
    class StrictModel(BaseModel):
        name: str
        count: int

    data = b'{"$type": "StrictModel", "name": 123, "count": "not-a-number"}'
    serializer = MessageSerialize()
    serializer.register_type(StrictModel)

    # when
    result = serializer.deserialize(data)

    # then
    assert isinstance(result, ValidationError)
    assert result.type_name == "StrictModel"
    assert result.fields == {"name": 123, "count": "not-a-number"}
