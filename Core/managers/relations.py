from ..common import RelationLayer
from ..entity import GameID, PlayerID, CardID, CharacterID, SkillID, ArmID, StatusID


class Relations:
    """
    多层级关系管理器，仅作为容器
    """

    def __init__(self) -> None:
        self.game = None
        self.players: RelationLayer[PlayerID, GameID] = RelationLayer[PlayerID, GameID]()
        # self.cards: RelationLayer[CardID, PlayerID] = RelationLayer[CardID, PlayerID]()
        self.characters: RelationLayer[CharacterID, PlayerID] = RelationLayer[CharacterID, PlayerID]()
        self.skills: RelationLayer[SkillID, CharacterID] = RelationLayer[SkillID, CharacterID]()
        # self.arms: RelationLayer[ArmID, CharacterID] = RelationLayer[ArmID, CharacterID]()
        self.statuses: RelationLayer[StatusID, CharacterID] = RelationLayer[StatusID, CharacterID]()

    def ready(self, game: GameID):
        self.game = game

    def clean_up(self) -> None:
        pass

    def clear(self):
        self.players.clear()
        # self.cards.clear()
        self.characters.clear()
        self.skills.clear()
        # self.arms.clear()
        self.statuses.clear()
