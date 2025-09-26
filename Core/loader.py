from tomllib import loads as toml_loads
from .entity import Player, Character, Skill, CharacterID, SkillID
from .gamesys import GameSys
from .common import uuid
from .effect import EffectSys


class GameLoader:
    def __init__(
            self,
            file_reload: bool,
            players: list[dict[str, str | list[str]]],
            gs: GameSys,
            es: EffectSys,
            character_config_path: str,
            skill_config_path: str,
    ):
        self.file_reload = file_reload
        self.players = players
        self.gs = gs
        self.es = es
        self.character_config_path = character_config_path
        self.skill_config_path = skill_config_path

        self.loaded: dict[str, dict] = {}

    def read_file(self, path: str):
        if path not in self.loaded or self.file_reload:
            with open(path, 'r', encoding='utf-8') as f:
                self.loaded[path] = toml_loads(f.read())

        return self.loaded[path]

    def read_character(self, character_name: str):
        path = f'{self.character_config_path}{character_name}.toml'

        return self.read_file(path)

    def read_skill(
            self,
            character_name: str,
            skill_slot: int
    ):
        path = f'{self.skill_config_path}{character_name}_{skill_slot}.toml'

        return self.read_file(path)

    def register_player(self, index: int):
        player_uuid = uuid()
        name = self.players[index]['name']
        player = Player(
            uuid=player_uuid,
            camp=player_uuid,
            name=name,
            display_name=name,
        )
        self.gs.register_player(player)
        for character_name in self.players[index]['characters']:
            self.register_character(character_name, player)

    def register_character(self, name: str, player: Player):
        character_uuid = uuid()
        character = Character(
            **self.read_character(name),
            uuid=character_uuid,
            camp=player.camp,
        )
        self.gs.register_character(character, player)
        for i in range(1, 3):
            self.register_skill(i, character)

    def register_skill(self, slot: int, character: Character):
        skill_uuid = uuid()
        skill = Skill(
            **self.read_skill(character.name, slot),
            uuid=skill_uuid,
            camp=character.camp,
            slot=slot
        )
        self.gs.register_skill(skill, character)
        skill.container.uuid = skill_uuid
        self.es.load_container(
            caster=CharacterID(character.uuid),
            belong=SkillID(skill.uuid),
            container=skill.container,
        )

    def ready(self):
        self.gs.ready()
        for i in range(2):
            self.register_player(i)

    def clear(self):
        self.gs.clear()
        self.es.clear()
