import typing
from dataclasses import dataclass, field
from datetime import datetime

from pytz import utc

from .types import CUSTOM_TYPES

try:
    import faust
except ImportError:  # pragma: no cover
    faust = None  # type: ignore # pragma: no cover

try:
    import pydantic  # pragma: no cover
except ImportError:  # type: ignore # pragma: no cover
    pydantic = None


def is_pydantic_model(klass: typing.Any) -> bool:
    if pydantic is not None:
        return issubclass(klass, pydantic.BaseModel)
    return False


def is_faust_model(klass: typing.Any) -> bool:
    if faust is not None:
        return issubclass(klass, faust.Record)
    return False


def is_union(a_type: typing.Any) -> bool:
    """
    Given a python type, return True if is typing.Union, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool
    """
    return isinstance(a_type, typing._GenericAlias) and a_type.__origin__ is typing.Union  # type: ignore


def is_self_referenced(a_type: typing.Any) -> bool:
    """
    Given a python type, return True if is self referenced, meaning
    that is instance of typing.ForwardRef, otherwise False

    Arguments:
        a_type (typing.Any): python type

    Returns:
        bool

    Example:
        a_type = typing.Type["User"]]

        is_self_referenced(a_type) # True
    """
    return (
        isinstance(a_type, typing._GenericAlias)  # type: ignore
        and a_type.__args__
        and isinstance(a_type.__args__[0], typing.ForwardRef)  # type: ignore
    )


def is_custom_type(value: typing.Any) -> bool:
    """
    Given a type, return True if is a custom type (Fixed, Decimal)
    """
    return isinstance(value, dict) and value.get("_dataclasses_custom_type") in CUSTOM_TYPES


@dataclass
class SchemaMetadata:
    schema_name: typing.Optional[str] = None
    schema_doc: bool = True
    namespace: typing.Optional[typing.List[str]] = None
    aliases: typing.Optional[typing.List[str]] = None
    alias_nested_items: typing.Dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(cls: typing.Any, klass: type) -> typing.Any:
        return cls(
            schema_name=getattr(klass, "schema_name", None),
            schema_doc=getattr(klass, "schema_doc", True),
            namespace=getattr(klass, "namespace", None),
            aliases=getattr(klass, "aliases", None),
            alias_nested_items=getattr(klass, "alias_nested_items", {}),
        )

    def get_alias_nested_items(self, name: str) -> typing.Optional[str]:
        return self.alias_nested_items.get(name)


@dataclass
class FieldMetadata:
    aliases: typing.List[str] = field(default_factory=list)
    doc: typing.Optional[str] = None
    namespace: typing.Optional[str] = None

    @classmethod
    def create(cls: typing.Any, klass: type) -> "FieldMetadata":
        return cls(
            aliases=getattr(klass, "aliases", []),
            doc=getattr(klass, "doc", None),
            namespace=getattr(klass, "namespace", None),
        )

    def to_dict(self) -> typing.Dict[str, typing.Union[typing.List[str], str]]:
        return {key: value for key, value in vars(self).items() if value}


class UserDefinedType(typing.NamedTuple):
    name: str
    type: typing.Any


epoch: datetime = datetime(1970, 1, 1, tzinfo=utc)
epoch_naive: datetime = datetime(1970, 1, 1)
