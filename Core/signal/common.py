from typing import TypeVar, Callable, TypeAlias

ArgT = TypeVar('ArgT')

CallbackT: TypeAlias = Callable[[ArgT], None]
CheckT: TypeAlias = Callable[[ArgT], bool]
FinalT: TypeAlias = Callable[[], None]
