from typing import Generic, TypeVar, Hashable

T = TypeVar('T', bound=Hashable)


class MultiLock(Generic[T]):
    """
    多独立锁
    """

    def __init__(self, allowed: set[T]):
        self._allowed: set[T] = allowed
        self._locks: set[T] = set()

    def lock(self, flag: T) -> None:
        """加锁，相同 flag 重复锁定仅视为一次有效锁定"""
        if flag in self._allowed:
            self._locks.add(flag)
        else:
            raise RuntimeError(f'unknown lock {flag}')

    def unlock(self, flag: T) -> None:
        """解锁，相同 flag 重复锁定仅视为一次有效解锁"""
        if flag in self._allowed:
            self._locks.discard(flag)
        else:
            raise RuntimeError(f'unknown lock {flag}')

    def has_lock(self, flag: T) -> bool:
        """锁 flag 是否在生效"""
        if flag in self._allowed:
            return flag in self._locks
        else:
            raise RuntimeError(f'unknown lock {flag}')

    def is_active(self) -> bool:
        """是否在锁定"""
        return bool(self._locks)
