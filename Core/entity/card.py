from .entity import Entity, EntityTags, EntityID


class Card(Entity):
    cost: int = -1
    """花费"""


class CardTags(EntityTags):
    pass


class CardID(EntityID): pass
