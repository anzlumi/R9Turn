import random
import tomllib

from mypy.typeops import false_only

from Core import EffectSys
from Core import GameLoader
from Core import GameSys
from Core.entity import ContainerID, CharacterID


class GameProcess:
    def __init__(self, seed=1999):
        self.seed = seed
        with open('config.toml', 'r', encoding='utf-8') as f:
            config = tomllib.loads(f.read())

        self.gs = GameSys()
        self.gs.print_signal_args = config['gamesys']['print_signal_args']

        self.es = EffectSys()
        self.loader = GameLoader(
            **(config['loader']),
            gs=self.gs,
            es=self.es,
        )

        self.ready()

    def get_allowed_skills(self):
        res = self.gs.get_allowed_skills()
        return res

    def get_need_selections(self, skillid: int):
        containerid = ContainerID(skillid)
        original_list = self.es.export_container_need(containerid)
        new_list = [
            (first_element, [char_id.uuid for char_id in char_set])
            for first_element, char_set in original_list
        ]
        return new_list

    def run_container(self, containerid: int, selections: list[list[int]]):
        self.es.run_container(
            ContainerID(containerid),
            selections=[
                [
                    CharacterID(uuid)
                    for uuid in selector
                ]
                for selector in selections
            ],
        )

        return self.gs.export_dict()

    def rand_run(self, playerid: int) -> int:
        allowed = self.get_allowed_skills()[playerid]
        skills = [key for inner_dict in allowed.values() for key, v in inner_dict.items() if v]
        if len(skills) == 0:
            return playerid
        else:
            skill = random.choice(skills)
            need = self.get_need_selections(skill)
            self.run_container(
                skill,
                [random.sample(selections, k=num) if selections else [] for num, selections in need]
            )
            return 0

    def get_dict(self):
        return self.gs.export_dict()

    def ready(self):
        """重新加载准备"""
        random.seed(self.seed)
        with open('config.toml', 'r', encoding='utf-8') as f:
            config = tomllib.loads(f.read())

        self.gs = GameSys()
        self.gs.print_signal_args = config['gamesys']['print_signal_args']

        self.es = EffectSys()
        self.loader = GameLoader(
            **(config['loader']),
            gs=self.gs,
            es=self.es,
        )
        self.loader.ready()

    def load(self):
        """不重载准备"""
        self.loader.ready()

    def turn_start(self):
        self.gs.turn_start()

    def process(self):
        self.gs.process()
        self.gs.clean_up()

    def clear(self):
        self.loader.clear()

    def export_player_id(self):
        players = self.gs.relations.players.get_item_list()
        return [player.uuid for player in players]

    def export_character_id(self):
        characters = self.gs.relations.characters.get_all_items()
        return [characters.uuid for characters in characters]

    def export_character_hp(self):
        characters = self.gs.relations.characters.get_all_items()
        return [
            self.gs.attributes.characters.hp.current(character)
            for character in characters
        ]

    def print_character_hp(self, space: int = 4):
        hps = self.export_character_hp()
        hp_header = "hp".ljust(space)

        formatted_hps = [str(hp).ljust(space) for hp in hps]

        result = hp_header + ''.join(formatted_hps)
        print(result)

    def simulate(self, player_index: int = -1, max_turn=50) -> tuple[int, int]:
        """返回战败方"""

        if self.loader.file_reload:
            self.loader.file_reload = False
            # print('[Simulate] 模拟已自动关闭文件重读')

        players = self.export_player_id()
        player_index = random.randint(0, 1) if player_index not in [0, 1] else player_index

        self.clear()
        self.load()
        turn = 1

        while turn <= max_turn:
            self.turn_start()
            res = self.rand_run(players[player_index])
            if res:
                return players.index(res), turn

            player_index = 1 - player_index
            res = self.rand_run(players[player_index])
            if res:
                return players.index(res), turn

            player_index = 1 - player_index
            self.process()
            turn += 1

        return -1, turn


if __name__ == '__main__':
    gp = GameProcess()
    pass
