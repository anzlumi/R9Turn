from .common import (
    ValueT,
    ArgRx,
)
from .rxpers import RxPers
from ..entity import EntityID
from ..signal import SignalBus


class RxTemp(RxPers[ValueT]):
    """
    非持久化响应对象
    """

    def __init__(self, signal_bus: SignalBus) -> None:
        super().__init__(signal_bus)

        self.dynamic_values: dict[EntityID, ValueT] = {}

    def register(self, target: EntityID, value: ValueT) -> 'RxTemp[ValueT]':
        self.values[target] = value
        self.dynamic_values[target] = value

        return self

    def request(self, entity: EntityID) -> ValueT:
        if entity not in self.values:
            raise ValueError(f'Unknown entity {entity.uuid}')

        arg: ArgRx[ValueT] = ArgRx[ValueT](
            value=self.values[entity],
            target=entity,
        )

        self.signal_bus.emit(
            signal=self.signal,
            arg=arg,
        )

        self.dynamic_values[entity] = arg.current()

        return self.dynamic_values[entity]

    def current(self, entity: EntityID) -> ValueT:
        if entity not in self.values:
            raise ValueError(f'Unknown entity {entity.uuid}')

        return self.dynamic_values[entity]
