from typing import Optional, Literal

from .container import Container
from .entity import Entity, EntityTags, EntityID

SkillTypeEnum = Literal[
    'health',
    'buff',
    'attack',
    'debuff',
    'special',
]


class Skill(Entity):
    slot: int
    """槽位"""
    lvl: int = -1
    """卡牌等级，用于索引 Container"""
    skill_type: SkillTypeEnum
    """技能类型"""
    cost: int = -1
    """技能花费"""
    container: Container
    """容器"""
    usable: bool = False
    """能否使用"""

    def ready(self) -> None:
        self.usable = True


class SkillTags(EntityTags):
    slot: Optional[set[int] | int] = None
    lvl: Optional[set[int] | int] = None
    skill_type: Optional[set[str] | str] = None
    cost: Optional[set[int] | int] = None
    useable: Optional[set[bool] | bool] = False


class SkillID(EntityID): pass
