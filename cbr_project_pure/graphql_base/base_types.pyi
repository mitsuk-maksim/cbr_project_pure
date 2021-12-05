from datetime import time, datetime, date
import enum
from typing import Any, Tuple, TypeVar, Optional, overload, Literal, List as ListType, Type

from django.contrib.auth.models import User
from django.http import HttpRequest

import graphene
from graphql import ResolveInfo
from typing_extensions import Protocol

_I = TypeVar('_I', bound=enum.Enum)


class _EnumProtocol(graphene.Enum):
    def from_enum(self, type: Type[_I]) -> Type[_I]: ...


Enum: _EnumProtocol = ...


_R = TypeVar('_R')

_T = TypeVar('_T')

_C = TypeVar('_C')

_D = TypeVar('_D')

_F = TypeVar('_F')


class _InputObjectCallableProtocol(Protocol[_F]):
    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[_F]: ...

    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[_F]: ...

    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> _F: ...


class _ObjectTypeCallableProtocol(Protocol[_F]):
    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[_F]: ...

    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[_F]: ...

    @overload
    def __call__(
            self: Type[_F], *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> _F: ...


_E = TypeVar('_E', int, str, bool, float, datetime, time, date, list, dict)

InputObjectType: _InputObjectCallableProtocol = ...

_V = TypeVar('_V', bound=InputObjectType)


class _CallableProtocol(Protocol[_E]):
    @overload
    def __call__(self, *args: Tuple[Any], required: Literal[True], **kwargs: Any) -> _E: ...

    @overload
    def __call__(self, *args: Tuple[Any], required: Literal[False], **kwargs: Any) -> Optional[_E]: ...

    @overload
    def __call__(self, *args: Tuple[Any], required: None = None, **kwargs: Any) -> Optional[_E]: ...


class _ArgumentCallableProtocol(Protocol):
    @overload
    def __call__(self, type: Type[_E], required: Literal[True], **kwargs: Any) -> _E: ...

    @overload
    def __call__(self, type: Type[_E], required: Literal[False], **kwargs: Any) -> Optional[_E]: ...

    @overload
    def __call__(self, type: Type[_E], required: None = None, **kwargs: Any) -> Optional[_E]: ...

    @overload
    def __call__(self, type: Type[_I], required: Literal[True], **kwargs: Any) -> _I: ...

    @overload
    def __call__(self, type: Type[_I], required: Literal[False], **kwargs: Any) -> Optional[_I]: ...

    @overload
    def __call__(self, type: Type[_I], required: None = None, **kwargs: Any) -> Optional[_I]: ...

    @overload
    def __call__(self, type: Type[_V], required: Literal[True], **kwargs: Any) -> _V: ...

    @overload
    def __call__(self, type: Type[_V], required: Literal[False], **kwargs: Any) -> Optional[_V]: ...

    @overload
    def __call__(self, type: Type[_V], required: None = None, **kwargs: Any) -> Optional[_V]: ...

    @overload
    def __call__(self, type: _CallableProtocol[_R], required: Literal[True], **kwargs: Any) -> _R: ...

    @overload
    def __call__(self, type: _CallableProtocol[_R], required: Literal[False], **kwargs: Any) -> Optional[_R]: ...

    @overload
    def __call__(self, type: _CallableProtocol[_R], required: None = None, **kwargs: Any) -> Optional[_R]: ...


Argument: _ArgumentCallableProtocol = ...

ObjectType: _ObjectTypeCallableProtocol = ...


_G = TypeVar('_G', bound=ObjectType)


class _FieldProtocol(Protocol[_D]):
    @overload
    def __call__(self, type: Type[_D], required: Literal[True], **kwargs: Any) -> _D: ...

    @overload
    def __call__(self, type: Type[_D], required: Literal[False], **kwargs: Any) -> Optional[_D]: ...

    @overload
    def __call__(self, type: Type[_D], required: None = None, **kwargs: Any) -> Optional[_D]: ...

    @overload
    def __call__(self, type: str, required: Literal[True], **kwargs: Any) -> _ObjectTypeCallableProtocol: ...

    @overload
    def __call__(self, type: str, required: Literal[False], **kwargs: Any) -> Optional[_ObjectTypeCallableProtocol]: ...

    @overload
    def __call__(self, type: str, required: None = None, **kwargs: Any) -> Optional[_ObjectTypeCallableProtocol]: ...


class _NonNullProtocol(Protocol[_C]):
    @overload
    def __call__(self, type: _CallableProtocol[_C], **kwargs: Any) -> _C: ...

    @overload
    def __call__(self, type: Optional[_E], **kwargs: Any) -> _E: ...

    @overload
    def __call__(self, type: Type[_G], **kwargs: Any) -> _G: ...

    @overload
    def __call__(self, type: Type[_I], **kwargs: Any) -> _I: ...


class _ListProtocol(Protocol[_R]):
    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> ListType[Optional[_R]]: ...

    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[ListType[Optional[_R]]]: ...

    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[ListType[Optional[_R]]]: ...

    @overload
    def __call__(
            self, type: _E, *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> ListType[_E]: ...

    @overload
    def __call__(
            self, type: _E, *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[ListType[_E]]: ...

    @overload
    def __call__(
            self, type: _E, *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[ListType[_E]]: ...

    @overload
    def __call__(
            self, type: Type[_R], *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> ListType[Optional[_R]]: ...

    @overload
    def __call__(
            self, type: Type[_R], *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[ListType[Optional[_R]]]: ...

    @overload
    def __call__(
            self, type: Type[_R], *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[ListType[Optional[_R]]]: ...

    @overload
    def __call__(
            self, type: _G, *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> ListType[_G]: ...

    @overload
    def __call__(
            self, type: _G, *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[ListType[_G]]: ...

    @overload
    def __call__(
            self, type: _G, *args: Tuple[Any],
            required: None = None, **kwargs: Any
    ) -> Optional[ListType[_G]]: ...


class _InputFieldProtocol(Protocol[_R]):
    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: Literal[True], **kwargs: Any
    ) -> _R: ...

    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: Literal[False], **kwargs: Any
    ) -> Optional[_R]: ...

    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            required: None = None, default_value: None = None, **kwargs: Any
    ) -> Optional[_R]: ...

    @overload
    def __call__(
            self, type: _CallableProtocol[_R], *args: Tuple[Any],
            default_value: _R, **kwargs: Any
    ) -> _R: ...


InputField: _InputFieldProtocol = ...

Int: _CallableProtocol[int] = ...

Float: _CallableProtocol[float] = ...

Time: _CallableProtocol[time] = ...

String: _CallableProtocol[str] = ...

ID: _CallableProtocol[str] = ...

DateTime: _CallableProtocol[datetime] = ...

Date: _CallableProtocol[date] = ...

Boolean: _CallableProtocol[bool] = ...

JSONString: _CallableProtocol[dict] = ...

ListOf: _ListProtocol = ...

Field: _FieldProtocol = ...

NN: _NonNullProtocol = ...


class _RequestContext(HttpRequest):
    @property
    def user(self) -> Optional[User]: ...


class _ResolveInfo(ResolveInfo):
    @property
    def context(self) -> _RequestContext: ...


ResolveInfo: _ResolveInfo = ...
