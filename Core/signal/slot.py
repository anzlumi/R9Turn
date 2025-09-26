from enum import Enum, auto
from typing import Generic, Optional

from .common import (
    ArgT,
    CallbackT,
    CheckT,
    FinalT,
)
from .multi_lock import MultiLock


class Delay(Enum):
    COMMON = auto()
    DURATION = auto()
    TIMES = auto()


class Pause(Enum):
    COMMON = auto()
    SIGNAL = auto()


class Slot(Generic[ArgT]):
    """
    维护了信号回调的工具类，本身不作为信号回调的标识符

    回调对信号的响应有三种，分别是广播、命中、执行

    1. 广播，一个信号维护多个回调对象，信号会尝试对所有活动回调进行广播

    2. 命中，然而信号中的回调是混杂的，有时有些回调并不应该被调用，又避免信号过多，所以用 Slot.check 判断是否命中

    3. 执行，回调接受参数，具体执行

    + 若 is_active() 为 Fals，则拒绝所有行为，是程序中删除的标记

    + 使用 pause 以外部阻止信号的命中，使用 check 内部阻止信号的命中

    + 只要被广播到，都会执行 final

    + pause 或 delay 各自的锁不应内部依赖，避免死锁
    """

    def __hash__(self) -> int:
        return hash(id(self))

    def __init__(
            self,
            callback: CallbackT[ArgT],
            check: Optional[CheckT[ArgT]] = None,
            final: Optional[FinalT] = None,
            duration: int = -1,
            times: int = -1,
            duration_delay: int = 0,
            times_delay: int = 0,
    ) -> None:
        """
        :param duration: 回合数，-1 表示永远触发，0 表示不触发，其他正数表示持续回合数，由 process 函数驱动
        :param times: 最大触发次数，-1 表示永远触发，0 表示不触发，其他正数表示触发次数，由 emit 自动处理
        :param duration_delay: 延迟，0 表示无延迟，其他正数表示延迟回合数，由 process 驱动
        :param times_delay: 延迟，0 表示无延迟，其他正数表示延迟次数，命中即减少
        """
        self.callback: CallbackT[ArgT] = callback
        self.check: Optional[CheckT[ArgT]] = check
        self.final: Optional[FinalT] = final
        self._duration: int = duration
        self._times: int = times
        self._duration_delay: int = duration_delay
        self._times_delay: int = times_delay

        self._active: bool = True
        self._paused: MultiLock[Pause] = MultiLock[Pause](set(Pause))
        self._delayed: MultiLock[Delay] = MultiLock[Delay](set(Delay))

        self.update(
            duration=duration,
            times=times,
            duration_delay=duration_delay,
            times_delay=times_delay,
        )

    def update(
            self,
            duration: int = -1,
            times: int = -1,
            duration_delay: int = 0,
            times_delay: int = 0,
    ) -> bool:
        if not self._active:
            return False

        if duration < -1:
            raise ValueError('invalid slot duration')
        if times < -1:
            raise ValueError('invalid slot times')
        if duration_delay < 0:
            raise ValueError('invalid slot duration_delay')
        if times_delay < 0:
            raise ValueError('invalid slot times_delay')

        self._duration = duration
        self._times = times
        self._duration_delay = duration_delay
        self._times_delay = times_delay

        if self._duration == 0 or self._times == 0:
            self.deactivate()
        if self._duration_delay > 0:
            self.enable_delay(Delay.DURATION)
        if self._times_delay > 0:
            self.enable_delay(Delay.TIMES)

        return True

    def enable_delay(self, flag: Delay) -> bool:
        if (
                not self._active or
                self._paused.is_active()
        ):
            return False

        self._delayed.lock(flag)
        return True

    def disable_delay(self, flag: Delay) -> bool:
        if (
                not self._active or
                self._paused.is_active()
        ):
            return False

        self._delayed.unlock(flag)
        return True

    def has_delay(self, flag: Delay) -> bool:
        return self._delayed.has_lock(flag)

    def is_delayed(self) -> bool:
        return self._delayed.is_active()

    def enable_pause(self, flag: Pause) -> bool:
        if not self._active:
            return False

        self._paused.lock(flag)
        return True

    def disable_pause(self, flag: Pause) -> bool:
        if not self._active:
            return False

        self._paused.unlock(flag)
        return True

    def has_paused(self, flag: Pause) -> bool:
        return self._paused.has_lock(flag)

    def is_paused(self) -> bool:
        return self._paused.is_active()

    def deactivate(self) -> None:
        """使 Slot 直接失效，不允许再次激活"""
        if self._active and self.final:
            self.final()
        self._active = False

    def is_active(self) -> bool:
        return self._active

    def is_callable(self) -> bool:
        """是否可以执行回调"""
        return (
                self._active and
                not self._paused.is_active() and
                not self._delayed.is_active()
        )

    def call(self, arg: ArgT) -> bool:
        if not self._active:
            return False

        if (
                self._delayed.is_active() or
                (self.check and not self.check(arg))
        ):
            return False

        if not self._delayed.is_active():
            self.callback(arg)
            self.decrease_times()
            return True

        self.decrease_times()
        return False

    def __call__(self, arg: ArgT) -> bool:
        return self.call(arg)

    def decrease_times(self) -> None:
        if (
                not self._active or
                self._paused.is_active()
        ):
            return

        if self._times_delay > 0:
            self._times_delay -= 1
            if self._times_delay == 0:
                self.disable_delay(Delay.TIMES)
        elif self._times > 0:
            self._times -= 1
            if self._times == 0:
                self.deactivate()

    def process(self) -> None:
        if (
                not self._active or
                self._paused.is_active()
        ):
            return

        if self._duration_delay > 0:
            self._duration_delay -= 1
            if self._duration_delay == 0:
                self.disable_delay(Delay.DURATION)
        elif self._duration != -1:
            self._duration -= 1
            if self._duration == 0:
                self.deactivate()
