from .effectsys import EffectSys
from ..common import uuid
from ..entity import Effect, CharacterT, NumT, CharacterID, Status, AttributeT, StatusTags
from ..gamesys import GameSys
from ..rxsys import ArgRx, entity_equal, irxpers_once
from ..signal import Slot

es: EffectSys = EffectSys()
gs: GameSys = GameSys()


@es.register(
    name='直伤',
    description='对{targets}造成攻击+({value})伤害',
)
class EffDirDamage(Effect):
    caster: CharacterT
    targets: CharacterT
    value: NumT

    def run(self) -> None:
        if self.caster is None or self.targets is None:
            raise RuntimeError('uninitialized effect')

        if len(self.caster) != 1:
            raise RuntimeError('invalid caster')

        for target in self.targets:
            if not gs.attributes.characters.alive.request(target):
                continue

            gs.take_damage_character(
                value=self.value,
                target=target,
                source=self.caster[0],
                damage_type='common',
            )


@es.register(
    name='回合属性修改',
    description='{duration}回合内{target}{attribute}{value}}',
)
class EffAtkEnh(Effect):
    duration: NumT
    targets: CharacterT
    value: NumT
    attribute: AttributeT
    _added: dict[CharacterID, Slot] = {}

    def _clear(self, target: CharacterID):
        def _callback() -> None:
            self._added.pop(target, None)

        return _callback

    @staticmethod
    def _add_value(value: int):
        def _callback(arg: ArgRx[int]):
            arg.append(max(arg.current() + value, 0))

        return _callback

    def run(self) -> None:
        if self.targets is None:
            raise RuntimeError('uninitialized effect')

        characters = gs.attributes.characters
        if self.attribute == 'attack':
            attr = characters.attack
        elif self.attribute == 'defense':
            attr = characters.defense
        elif self.attribute == 'max_hp':
            attr = characters.max_hp
        else:
            raise RuntimeError('invalid attribute')

        for target in self.targets:
            if not gs.attributes.characters.alive.request(target):
                continue

            # 避免重复施加
            if target in self._added:
                self._added[target].deactivate()

            slot = Slot[ArgRx[int]](
                callback=self._add_value(self.value),
                check=entity_equal(target),
                final=self._clear(target),
                duration=self.duration,
                times=-1
            )
            self._added[target] = slot
            attr.add_slot(slot=slot)

    def clear(self) -> None:
        self._added.clear()


@es.register(
    name='中毒',
    description='使{targets}进入中毒状态，持续{duration}回合，回合结束时受到{value}点伤害',
)
class EffPoison(Effect):
    caster: CharacterT
    targets: CharacterT
    duration: NumT
    value: NumT

    def _poison(self, target: CharacterID):
        def _callback(_: None) -> None:
            gs.take_damage_direct(
                damage=self.value,
                target=target,
                source=self.caster[0],
                damage_type='status',
            )

        return _callback

    def run(self) -> None:
        if self.caster is None or self.targets is None:
            raise RuntimeError('uninitialized effect')

        if len(self.caster) != 1:
            raise RuntimeError('invalid caster')

        for target in self.targets:
            if not gs.attributes.characters.alive.request(target):
                continue

            slot = Slot[None](
                callback=self._poison(target=target),
                duration=self.duration,
                times=-1,
            )
            gs.signals.pre_turn_end.connect_slot(slot=slot)
            status = Status(
                uuid=uuid(),
                name='中毒',
                status_type={'异常'}
            )
            gs.add_status(
                status=status,
                source=self.caster[0],
                target=target,
                slots=[slot],
                ready=None,
            )


@es.register(
    name='治疗',
    description='回复{targets}{value}生命',
)
class EffHealth(Effect):
    caster: CharacterT
    targets: CharacterT
    value: NumT

    def run(self) -> None:
        if self.caster is None or self.targets is None:
            raise RuntimeError('uninitialized effect')

        if len(self.caster) != 1:
            raise RuntimeError('invalid caster')

        for target in self.targets:
            if not gs.attributes.characters.alive.request(target):
                continue

            gs.health(
                source=self.caster[0],
                target=target,
                value=self.value
            )


@es.register(
    name='解除中毒补偿生命调整',
    description='解除{targets}中毒状态，成功则令{later_targets}生命{value}',
)
class EffDePosHp(Effect):
    caster: CharacterT
    targets: CharacterT
    later_targets: CharacterT
    value: NumT

    def run(self) -> None:
        if self.caster is None or self.targets is None:
            raise RuntimeError('uninitialized effect')

        if len(self.caster) != 1:
            raise RuntimeError('invalid caster')

        flag = False  # 是否有效解除

        for target in self.targets:
            if not gs.attributes.characters.alive.request(target):
                continue

            status = gs.relations.statuses.get_children(target).copy()
            status &= gs.tags.statuses.select(StatusTags(name='中毒').export_tags())
            if len(status) == 0:
                continue

            for s in status:
                if gs.remove_status(
                        status=s,
                        source=self.caster[0],
                ):
                    flag = True

        if flag:
            for target in self.later_targets:
                irxpers_once(
                    gs.attributes.characters.hp,
                    value=self.value,
                    target=target,
                )
                # gs.health(
                #     source=self.caster[0],
                #     target=self.caster[0],
                #     value=self.value
                # )
