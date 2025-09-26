from ..entity import EntityID, Player, PlayerID
from ..rxsys import RxPers, RxTemp
from ..signal import SignalBus


class AttrPlayer:
    def __init__(self, signal_bus: SignalBus):
        self.signal_bus: SignalBus = signal_bus

        self.players: dict[PlayerID, Player] = {}

        # self.inspiration: RxPers[int] = RxPers[int](signal_bus)

        # self.max_inspiration: RxTemp[int] = RxTemp[int](signal_bus)

    def register(self, player: Player) -> None:
        entityid = EntityID(player.uuid)

        self.players[PlayerID(player.uuid)] = player

        # self.inspiration.register(entityid, 0)

        # self.max_inspiration.register(entityid, player.max_inspiration)

    def export_current(self, playerid: PlayerID) -> Player:
        player = self.players[playerid]
        return player.model_copy(
            update={
                # 'inspiration': self.inspiration.request(playerid),
                # 'max_inspiration': self.max_inspiration.request(playerid)
            }
        )
