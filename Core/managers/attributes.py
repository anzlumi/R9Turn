from .attr_character import AttrCharacter
from .attr_player import AttrPlayer
from .attr_skill import AttrSkill
from .attr_status import AttrStatus
from ..signal import SignalBus


class Attributes:
    def __init__(self, signal_bus: SignalBus):
        self.characters: AttrCharacter = AttrCharacter(signal_bus)
        self.players: AttrPlayer = AttrPlayer(signal_bus)
        self.skills: AttrSkill = AttrSkill(signal_bus)
        self.statuses: AttrStatus = AttrStatus(signal_bus)
