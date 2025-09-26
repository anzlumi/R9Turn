from .entity import Entity, EntityTags, EntityID


class Player(Entity):
    max_inspiration: int = -1
    """最大灵感"""
    inspiration: int = -1
    """当前灵感"""

    def ready(self) -> None:
        # self.inspiration = 0
        pass


class PlayerTags(EntityTags):
    pass


class PlayerID(EntityID): pass
