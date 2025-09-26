from .entity import Entity, EntityTags, EntityID


class Game(Entity):
    turn: int = 0

    def ready(self) -> None:
        self.turn = 0

    def process(self) -> None:
        self.turn += 1


class GameTags(EntityTags):
    pass


class GameID(EntityID): pass
