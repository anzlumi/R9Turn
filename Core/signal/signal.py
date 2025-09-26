from typing import Generic, Callable, TypeAlias, Optional

from .common import (
    ArgT,
    CallbackT,
    CheckT,
    FinalT,
)
from .slot import Slot

AssignerT: TypeAlias = Callable[[], int]


class Signal(Generic[ArgT]):
    """
    信号，考虑外部执行顺序需要，允许传递序号分配器
    """

    def __init__(self, name='', assigner: Optional[AssignerT] = None) -> None:
        self.name: str = name
        self.assigner: AssignerT = self._get_order if assigner is None else assigner
        self._order: int = 0
        self.cb_order: dict[CallbackT[ArgT], int] = {}
        self.orders: dict[int, tuple[int, Slot[ArgT]]] = {}

    def __hash__(self) -> int:
        return hash(id(self))

    def _get_order(self) -> int:
        self._order += 1
        return self._order

    def disconnect(self, callback: CallbackT[ArgT]) -> Optional[Slot[ArgT]]:
        if callback not in self.cb_order:
            return None

        order: int = self.cb_order.pop(callback)
        _, slot = self.orders.pop(order)
        slot.deactivate()
        return slot

    def connect_slot(self, slot: Slot[ArgT]) -> Slot[ArgT]:
        order: int = self.assigner()
        self.cb_order[slot.callback] = order
        self.orders[order] = (order, slot)

        return slot

    def connect(
            self,
            callback: CallbackT[ArgT],
            check: Optional[CheckT[ArgT]] = None,
            final: Optional[FinalT] = None,
            duration: int = -1,
            times: int = -1,
            duration_delay: int = 0,
            times_delay: int = 0,
    ) -> Slot[ArgT]:
        self.disconnect(callback)

        slot: Slot[ArgT] = Slot[ArgT](
            callback=callback,
            check=check,
            final=final,
            duration=duration,
            times=times,
            duration_delay=duration_delay,
            times_delay=times_delay,
        )

        return self.connect_slot(slot)

    def get_orders(self) -> dict[int, tuple[int, Slot[ArgT]]]:
        return self.orders

    def export_slots(self) -> list[Slot[ArgT]]:
        return list(slot for _, slot in sorted(self.orders.values()))

    def emit(self, arg: ArgT) -> None:
        for slot in self.export_slots():
            slot.call(arg)

    def process(self) -> None:
        for _, slot in self.orders.values():
            slot.process()

    def clean_up(self) -> None:
        for _, slot in list(self.orders.values()):
            if not slot.is_active():
                self.disconnect(slot.callback)

    def clear(self) -> None:
        self._order = 0
        self.cb_order.clear()
        self.orders.clear()

    def __repr__(self) -> str:
        if self.name:
            return self.name
        return super().__repr__()
