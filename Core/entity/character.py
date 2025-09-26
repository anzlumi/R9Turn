from typing import Optional, Literal, TypeAlias

from .entity import Entity, EntityTags, EntityID

AttributeT: TypeAlias = Literal[
    'max_hp',
    'hp',
    'max_passion',
    'passion',
    'inspiration',
    'attack',
    'defense',
]


class Character(Entity):
    max_hp: int
    """最大生命"""
    attack: int
    """攻击"""
    defense: int
    """防御"""
    inspiration: int = -1
    """灵感"""
    max_passion: int = -1
    """最大激情"""
    # ---------- 以上属性临时修改，以下属性持久化修改 ----------
    hp: int = 0
    """当前生命"""
    passion: int = -1
    """当前激情"""
    in_play: bool = True
    """是否登场"""
    alive: bool = False
    """是否存活"""

    def ready(self) -> None:
        self.hp = self.max_hp
        self.passion = 0
        self.alive = True


class CharacterTags(EntityTags):
    in_play: Optional[set[bool] | bool] = None
    alive: Optional[set[bool] | bool] = None


class CharacterID(EntityID): pass
