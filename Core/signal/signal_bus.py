from typing import Optional, Any

from .common import (
    ArgT,
    CallbackT,
    CheckT,
    FinalT,
)
from .signal import Signal
from .slot import Slot, Pause


class SignalBus:
    def __init__(self) -> None:
        self.signals: set[Signal[Any]] = set()
        self.start_dep: dict[Signal[Any], set[Slot[Any]]] = {}
        self.end_dep: dict[Signal[Any], set[Slot[Any]]] = {}

    def register(self, signal: Signal[Any]) -> 'SignalBus':
        self.signals.add(signal)
        return self

    def connect_slot(
            self,
            signal: Signal[ArgT],
            slot: Slot[ArgT],
            start_dep: Optional[Signal[Any]] = None,
            end_dep: Optional[Signal[Any]] = None,
    ) -> Slot[ArgT]:
        if signal not in self.signals:
            raise RuntimeError(f"signal {signal} not registered")
        if start_dep and start_dep not in self.signals:
            raise RuntimeError(f"signal {start_dep} not registered")
        if end_dep and start_dep not in self.signals:
            raise RuntimeError(f"signal {end_dep} not registered")

        signal.connect_slot(slot)

        # 无论是否循环依赖，只要 emit 都将解锁，所以无循环依赖问题
        if start_dep:
            self.start_dep.setdefault(start_dep, set()).add(slot)
            slot.enable_pause(Pause.SIGNAL)
        if end_dep:
            self.end_dep.setdefault(end_dep, set()).add(slot)

        return slot

    def connect(
            self,
            signal: Signal[ArgT],
            callback: CallbackT[ArgT],
            check: Optional[CheckT[ArgT]] = None,
            final: Optional[FinalT] = None,
            duration: int = -1,
            times: int = -1,
            duration_delay: int = 0,
            times_delay: int = 0,
            start_dep: Optional[Signal[Any]] = None,
            end_dep: Optional[Signal[Any]] = None,
    ) -> Slot[ArgT]:
        slot = signal.connect(
            callback=callback,
            check=check,
            final=final,
            duration=duration,
            times=times,
            duration_delay=duration_delay,
            times_delay=times_delay,
        )

        return self.connect_slot(
            signal=signal,
            slot=slot,
            start_dep=start_dep,
            end_dep=end_dep,
        )

    @staticmethod
    def disconnect(signal: Signal[ArgT], callback: CallbackT[ArgT]) -> Optional[Slot[ArgT]]:
        return signal.disconnect(callback)

    def emit(self, signal: Signal[ArgT], arg: ArgT) -> None:
        if signal in self.start_dep:
            for slot in self.start_dep.pop(signal):
                # 注意这里 pause 只依赖 active 所以无论是否清理成功，都不再保留
                slot.disable_pause(Pause.SIGNAL)

        if signal in self.end_dep:
            for slot in self.end_dep.pop(signal):
                slot.deactivate()

        signal.emit(arg)

    def process(self) -> None:
        for signal in self.signals:
            signal.process()

    def clean_up(self) -> None:
        for signal in self.signals:
            signal.clean_up()

        for signal, slots in list(self.start_dep.items()):
            active_slots = {slot for slot in slots if slot.is_active()}
            if active_slots:
                self.start_dep[signal] = active_slots
            else:
                self.start_dep.pop(signal)

        for signal, slots in list(self.end_dep.items()):
            active_slots = {slot for slot in slots if slot.is_active()}
            if active_slots:
                self.end_dep[signal] = active_slots
            else:
                self.end_dep.pop(signal)

    def clear(self):
        for signal in self.signals:
            signal.clear()
        self.start_dep.clear()
        self.end_dep.clear()
