from ..entity import StatusID, Status
from ..signal import SignalBus


class AttrStatus:
    def __init__(self, signal_bus: SignalBus):
        self.signal_bus: SignalBus = signal_bus

    def register(self, status: Status):
        pass

    def delete(self, status: StatusID):
        pass

    def export_current(self, status: StatusID):
        raise NotImplemented
