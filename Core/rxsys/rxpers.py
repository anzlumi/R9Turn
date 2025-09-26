from typing import Generic, Optional, Any

from .common import (
    ValueT,
    ArgRx,
    ArgT,
    CallbackT,
    CheckT,
    FinalT,
    entity_equal,
)
from ..entity import EntityID
from ..signal import SignalBus, Signal, Slot


class RxPers(Generic[ValueT]):
    """
    持久化响应式对象属性管理

    允许对多个同类对象的同一种属性进行管理
    """

    def __init__(self, signal_bus: SignalBus) -> None:
        self.values: dict[EntityID, ValueT] = {}

        self.signal_bus: SignalBus = signal_bus
        self.signal: Signal[ArgT[ValueT]] = Signal[ArgT[ValueT]]()

        self.signal_bus.register(self.signal)

    def register(self, target: EntityID, value: ValueT) -> 'RxPers[ValueT]':
        self.values[target] = value

        return self

    def add_slot(
            self,
            slot: Slot[ArgT[ValueT]],
            start_dep: Optional[Signal[Any]] = None,
            end_dep: Optional[Signal[Any]] = None,
    ) -> Slot[ArgT[ValueT]]:
        return self.signal_bus.connect_slot(
            signal=self.signal,
            slot=slot,
            start_dep=start_dep,
            end_dep=end_dep,
        )

    def add(
            self,
            callback: CallbackT[ValueT],
            check: Optional[CheckT[ValueT]] = None,
            final: Optional[FinalT] = None,
            duration: int = -1,
            times: int = 1,
            duration_delay: int = 0,
            times_delay: int = 0,
            start_dep: Optional[Signal[Any]] = None,
            end_dep: Optional[Signal[Any]] = None,
    ) -> Slot[ArgRx[ValueT]]:
        slot = Slot[ArgRx[ValueT]](
            callback=callback,
            check=check,
            final=final,
            duration=duration,
            times=times,
            duration_delay=duration_delay,
            times_delay=times_delay,
        )

        return self.add_slot(
            slot=slot,
            start_dep=start_dep,
            end_dep=end_dep
        )

    def request(self, entity: EntityID) -> ValueT:
        if entity not in self.values:
            raise ValueError(f'unknown target {entity.uuid}')

        arg: ArgRx[ValueT] = ArgRx[ValueT](
            value=self.values[entity],
            target=entity,
        )

        self.signal_bus.emit(
            signal=self.signal,
            arg=arg,
        )

        self.values[entity] = arg.current()

        return self.values[entity]

    def current(self, target: EntityID) -> ValueT:
        if target not in self.values:
            raise ValueError(f'unknown target {target.uuid}')

        return self.values[target]

    def get_signal(self) -> Signal[ArgT[ValueT]]:
        return self.signal

    def direct_modify(self, value: ValueT, target: EntityID) -> None:
        if target not in self.values:
            raise ValueError(f'unknown target {target.uuid}')

        self.values[target] = value


def irxpers_once(rxpers: RxPers[int], value: int, target: EntityID):
    """对 RxPers[int] 添加一次性修改"""

    def _modifier(arg: ArgRx[int]) -> None:
        arg.append(arg.current() + value)

    return rxpers.add(
        callback=_modifier,
        check=entity_equal(entity=target),
        times=1,
    )


def brxpers_once(rxpers: RxPers[bool], value: bool, target: EntityID) -> None:
    """对 RxPers[bool] 添加一次性修改"""

    def _modifier(arg: ArgRx[bool]) -> None:
        arg.append(value)

    rxpers.add(
        callback=_modifier,
        check=entity_equal(entity=target),
        times=1,
    )
