from dataclasses import dataclass
from typing import Literal

from ..entity import EntityID, CharacterID, StatusID, Status
from ..rxsys import RxPers
from ..signal import SignalBus, Signal

DamageType = Literal[
    'common',
    'real',
    'status',
]


@dataclass(kw_only=True)
class ArgDamageCollect:
    source: EntityID
    target: CharacterID
    damage_type: DamageType = 'common'


@dataclass(kw_only=True)
class ArgPreDamage:
    damage: int
    source: EntityID
    target: CharacterID
    damage_type: DamageType = 'common'


@dataclass(kw_only=True)
class ArgDamage:
    true_damage: int
    source: EntityID
    target: CharacterID
    damage_type: DamageType = 'common'


@dataclass(kw_only=True)
class ArgCouldAddStatus:
    effective: bool
    source: EntityID
    target: CharacterID
    status: Status


@dataclass(kw_only=True)
class ArgPreAddStatus:
    source: EntityID
    target: CharacterID
    status: Status


@dataclass(kw_only=True)
class ArgAddStatus:
    source: EntityID
    target: CharacterID
    status: StatusID


@dataclass(kw_only=True)
class ArgPreRemoveStatus:
    effective: bool
    source: EntityID
    status: StatusID


@dataclass(kw_only=True)
class ArgRemoveStatus:
    source: EntityID
    status: StatusID


@dataclass(kw_only=True)
class ArgDead:
    character: CharacterID
    source: EntityID


@dataclass(kw_only=True)
class ArgHealth:
    source: EntityID
    target: CharacterID
    value: int


class Signals:
    def __init__(self, signal_bus: SignalBus):
        self.signal_bus = signal_bus

        self.pre_turn_start: Signal[None] = Signal[None]('pre_turn_start')
        self.turn_start: Signal[None] = Signal[None]('turn_start')
        self.pre_turn_end: Signal[None] = Signal[None]('pre_turn_end')
        self.turn_end: Signal[None] = Signal[None]('turn_end')

        self.dead: Signal[ArgDead] = Signal[ArgDead]('dead')

        self.damage_collect: Signal[ArgDamageCollect] = Signal[ArgDamageCollect]('damage_collect')
        self.pre_damage: Signal[ArgPreDamage] = Signal[ArgPreDamage]('pre_damage')
        self.damage: Signal[ArgDamage] = Signal[ArgDamage]('damage')

        self.health: Signal[ArgHealth] = Signal[ArgHealth]('health')

        self.could_add_status: Signal[ArgCouldAddStatus] = Signal[ArgCouldAddStatus]('could_add_status')
        self.pre_add_status: Signal[ArgPreAddStatus] = Signal[ArgPreAddStatus]('pre_add_status')
        self.add_status: Signal[ArgAddStatus] = Signal[ArgAddStatus]('add_status')
        self.pre_remove_status: Signal[ArgPreRemoveStatus] = Signal[ArgPreRemoveStatus]('pre_remove_status')
        self.remove_status: Signal[ArgRemoveStatus] = Signal[ArgRemoveStatus]('remove_status')

        for field, value in self.__dict__.items():
            if isinstance(value, Signal):
                self.signal_bus.register(value)
