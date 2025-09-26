from ..entity import SkillID, Skill, EntityID
from ..rxsys import RxPers
from ..signal import SignalBus


class AttrSkill:
    def __init__(self, signal_bus: SignalBus):
        self.signal_bus: SignalBus = signal_bus

        self.skills: dict[SkillID, Skill] = {}

        self.usable: RxPers[bool] = RxPers[bool](signal_bus)

    def register(self, skill: Skill) -> None:
        entityid = EntityID(skill.uuid)

        self.skills[SkillID(skill.uuid)] = skill

        self.usable.register(entityid, skill.usable)

    def export_current(self, skillid: SkillID) -> Skill:
        skill = self.skills[skillid]
        return skill.model_copy(
            update={
                'usable': self.usable.request(skillid),
            }
        )
