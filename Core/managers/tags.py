from typing import TypeAlias

from ..common import TagsManager
from ..entity import CharacterID, PlayerID, SkillID, StatusID

TagT: TypeAlias = tuple[str, str]


class Tags:
    def __init__(self) -> None:
        self.players: TagsManager[PlayerID, TagT] = TagsManager[PlayerID, TagT]()
        self.characters: TagsManager[CharacterID, TagT] = TagsManager[CharacterID, TagT]()
        self.skills: TagsManager[SkillID, TagT] = TagsManager[SkillID, TagT]()
        self.statuses: TagsManager[StatusID, TagT] = TagsManager[StatusID, TagT]()

    def ready(self):
        raise NotImplemented

    def clean_up(self):
        self.players.clean_up()
        self.characters.clean_up()
        self.skills.clean_up()
        self.statuses.clean_up()

    def clear(self):
        self.players.clear()
        self.characters.clear()
        self.skills.clear()
        self.statuses.clear()
