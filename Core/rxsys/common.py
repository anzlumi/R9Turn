from typing import TypeVar, Generic, TypeAlias, Callable

from ..entity import EntityID

ValueT = TypeVar('ValueT')


class ArgRx(Generic[ValueT]):
    def __init__(self, value: ValueT, target: EntityID) -> None:
        self.history: list[ValueT] = [value]
        self.target: EntityID = target

    def current(self) -> ValueT:
        return self.history[-1]

    def append(self, value: ValueT) -> None:
        self.history.append(value)


ArgT: TypeAlias = ArgRx[ValueT]
CallbackT: TypeAlias = Callable[[ArgT[ValueT]], None]
CheckT: TypeAlias = Callable[[ArgT[ValueT]], bool]
FinalT: TypeAlias = Callable[[], None]


def entity_equal(entity: EntityID) -> CheckT[ValueT]:
    def _check(arg: ArgT[ValueT]) -> bool:
        return arg.target == entity

    return _check
