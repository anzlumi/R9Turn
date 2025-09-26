from typing import Optional, Literal, TypeAlias

from .entity import Entity, EntityTags, EntityID

StatusName: TypeAlias = Literal[
    '攻击强化',
    '中毒'
]
StatusT: TypeAlias = Literal[
    '增益',
    '减益',
    '控制',
    '异常',
]


class Status(Entity):
    name: StatusName
    """异常名"""
    status_type: set[StatusT] | StatusT
    """异常类型"""
    effective: bool = True
    """有效"""


class StatusTags(EntityTags):
    name: Optional[set[StatusName] | StatusName] = None
    status_type: Optional[set[StatusT] | StatusT] = None
    effective: bool = True


class StatusID(EntityID): pass
