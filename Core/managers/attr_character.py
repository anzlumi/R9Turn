from typing import Callable

from ..entity import Character, CharacterID
from ..rxsys import RxPers, RxTemp, ArgRx, entity_equal
from ..signal import SignalBus, Slot


class AttrCharacter:
    def __init__(self, signal_bus: SignalBus):
        self.signal_bus: SignalBus = signal_bus

        self.characters: dict[CharacterID, Character] = {}

        self.camp: RxPers[int] = RxPers[int](signal_bus)

        self.max_hp: RxTemp[int] = RxTemp[int](signal_bus)
        # self.inspiration: RxTemp[int] = RxTemp[int](signal_bus)
        self.attack: RxTemp[int] = RxTemp[int](signal_bus)
        self.defense: RxTemp[int] = RxTemp[int](signal_bus)
        # self.max_passion: RxTemp[int] = RxTemp[int](signal_bus)

        self.hp: RxPers[int] = RxPers[int](signal_bus)
        # self.passion: RxPers[int] = RxPers[int](signal_bus)
        self.in_play: RxPers[bool] = RxPers[bool](signal_bus)
        self.alive: RxPers[bool] = RxPers[bool](signal_bus)

    def alive_check(self, character: CharacterID) -> Callable[[ArgRx[bool]], None]:
        if character == CharacterID(16):
            pass
        def _checker(arg: ArgRx[bool]) -> None:
            if arg.current():
                arg.append(self.hp.current(character) > 0)
            else:
                arg.append(False)

        return _checker

    def register(self, character: Character) -> None:
        characterid = CharacterID(character.uuid)  # 显示转换

        self.characters[characterid] = character

        self.camp.register(characterid, character.camp)

        self.max_hp.register(characterid, character.max_hp)
        # self.inspiration.register(characterid, character.inspiration)
        self.attack.register(characterid, character.attack)
        self.defense.register(characterid, character.defense)
        # self.max_passion.register(characterid, character.max_passion)

        self.hp.register(characterid, character.hp)
        # self.passion.register(characterid, 0)
        self.in_play.register(characterid, character.in_play)
        self.alive.register(characterid, character.alive)

        self.alive.add(
            callback=self.alive_check(characterid),
            check=entity_equal(characterid),
            times=-1
        )

    def export_current(self, characterid: CharacterID) -> Character:
        character = self.characters[characterid]
        return character.model_copy(
            update={
                'camp': self.camp.request(characterid),
                'max_hp': self.max_hp.request(characterid),
                # 'inspiration': self.inspiration.request(characterid),
                'attack': self.attack.request(characterid),
                'defense': self.defense.request(characterid),
                # 'max_passion': self.max_passion.request(characterid),
                'hp': self.hp.request(characterid),
                # 'passion': self.passion.request(characterid),
                'in_play': self.in_play.request(characterid),
                'alive': self.alive.request(characterid),
            }
        )

    def modify_hp(self, delta: int, character: CharacterID) -> int:
        """
        在外部计算好生命修改后，内部直接修改生命

        对修改值合理性检查

        修改结束判断是否存活，注意这里不会发出 dead 信号

        :return 实际造成伤害
        """

        def _modifier(arg: ArgRx[int]) -> None:
            # 直接读取 alive/max_hp 避免无限循环
            alive = self.alive.current(arg.target)
            if arg.current() <= 0 or not alive:
                arg.append(0)
            else:
                max_hp = self.max_hp.current(arg.target)
                new_hp = min(arg.current() + delta, max_hp)
                new_hp = max(new_hp, 0)
                arg.append(new_hp)

        slot = Slot[ArgRx[int]](
            check=entity_equal(character),
            callback=_modifier,
            times=1,
        )

        old_hp = self.hp.current(character)
        self.hp.add_slot(slot=slot)
        self.hp.request(character)
        self.alive.request(character)
        return self.hp.current(character) - old_hp
