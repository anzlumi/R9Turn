from typing import TypeVar, Any, Callable, Optional, cast

from .common import singleton, uuid, UUID
from .entity import (
    Game, Character, Player, GameID, CharacterID, PlayerID,
    export_flat_tags, SelectorT, CharacterTags, EntityID, Skill, SkillID,
    Status, StatusID
)
from .managers import (
    Relations,
    Tags,
    Signals,
    Attributes,
    signals,
)
from .signal import SignalBus, Signal, Slot

ArgT = TypeVar("ArgT")


def signal_print(func):
    def _func(self, *args, **kwargs):
        if self.print_signal_args:
            print(f'[信号] {args} {kwargs}')
        func(self, *args, **kwargs)

    return _func


@singleton
class GameSys:
    def __init__(self) -> None:
        self.print_signal_args: bool = False
        self.game_info: Optional[Game] = None
        self.relations: Relations = Relations()
        self.tags: Tags = Tags()

        self.signal_bus: SignalBus = SignalBus()
        self.signals: Signals = Signals(self.signal_bus)
        self.attributes: Attributes = Attributes(self.signal_bus)

    def ready(self):
        game_uuid: int = uuid()
        self.game_info = Game(
            uuid=game_uuid,
            camp=game_uuid,
            name='game',
            display_name='Game',
        )
        self.relations.ready(GameID(game_uuid))
        # self.tags.ready()

    @signal_print
    def emit(self, signal: Signal[ArgT], arg: ArgT) -> None:
        self.signal_bus.emit(signal, arg)
        if signal == self.signals.dead:
            arg = cast(signals.ArgDead, arg)
            self.tags.characters.update(arg.character, self.export_character_tags(arg.character))

    def export_character_tags(self, characterid: CharacterID) -> set[tuple[str, str]]:
        new_attrs = self.attributes.characters.export_current(characterid)
        return export_flat_tags(new_attrs)

    def register_player(self, player: Player) -> None:
        player.ready()
        playerid = PlayerID(player.uuid)

        self.relations.players.add(playerid, self.relations.game)
        self.attributes.players.register(player)
        self.tags.players.add(playerid, export_flat_tags(player))

    def register_character(self, character: Character, player: Player) -> None:
        character.ready()
        characterid = CharacterID(character.uuid)

        self.relations.characters.add(characterid, PlayerID(player.uuid))
        self.attributes.characters.register(character)
        self.tags.characters.add(characterid, export_flat_tags(character))

    def register_skill(self, skill: Skill, character: Character) -> None:
        """注册技能的非效果部分，效果部分由 EffectSys解决"""
        skill.ready()
        skillid = SkillID(skill.uuid)

        self.relations.skills.add(skillid, CharacterID(character.uuid))
        self.attributes.skills.register(skill)
        self.tags.skills.add(skillid, export_flat_tags(skill))

    # 以上几个 register 是静态注册的，归属不使用 id，下者动态注册，用 id 对象
    def register_status(self, status: Status, character: CharacterID) -> StatusID:
        status.ready()
        statusid = StatusID(status.uuid)

        self.relations.statuses.add(statusid, character)
        self.attributes.statuses.register(status)
        self.tags.statuses.add(statusid, export_flat_tags(status))
        return statusid

    def delete_status(self, status: StatusID) -> None:
        self.relations.statuses.remove_item(status)
        self.attributes.statuses.delete(status)
        self.tags.statuses.remove_item(status)

    def take_damage_character(
            self,
            value: int,
            target: CharacterID,
            source: CharacterID,
            damage_type: signals.DamageType,
    ) -> int:
        attr = self.attributes.characters

        # ---------- 伤害计算收集 ----------
        arg_damage_collect = signals.ArgDamageCollect(
            target=target,
            source=source,
            damage_type=damage_type,
        )
        self.emit(self.signals.damage_collect, arg_damage_collect)
        attack = attr.attack.request(source)
        defense = attr.defense.request(target)
        damage = max(attack + value - defense, 0)

        return self.take_damage_direct(damage, target, source, damage_type)

    def take_damage_direct(
            self,
            damage: int,
            target: CharacterID,
            source: CharacterID,
            damage_type: signals.DamageType,
    ) -> int:
        """直接造成伤"""
        attr = self.attributes.characters
        # ---------- 预伤害处理 ----------
        damage = max(damage, 0)
        arg_pre_damage = signals.ArgPreDamage(
            damage=damage,
            target=target,
            source=source,
            damage_type=damage_type,
        )
        self.emit(self.signals.pre_damage, arg_pre_damage)
        damage = max(arg_pre_damage.damage, 0)
        # ---------- 实际伤害 ----------
        true_damage = -attr.modify_hp(delta=-damage, character=target)
        arg_damage = signals.ArgDamage(
            true_damage=true_damage,
            target=target,
            source=source,
            damage_type=damage_type,
        )
        self.emit(self.signals.damage, arg_damage)

        alive = self.attributes.characters.alive.request(target)
        if not alive:
            self.emit(
                self.signals.dead,
                signals.ArgDead(
                    character=target,
                    source=source,
                )
            )

        return true_damage

    def character_selector(self, caster: EntityID, preset: SelectorT) -> tuple[int, set[CharacterID]]:
        select = self.tags.characters.select
        attrs = self.attributes.characters
        if isinstance(caster, CharacterID):
            camp = attrs.camp.request(caster)
        elif isinstance(caster, PlayerID):
            camp = self.attributes.players.players[caster].uuid
        else:
            raise RuntimeError(f"Unknown caster type of {caster}")

        if preset == 'caster' and isinstance(caster, CharacterID):
            return 1, {caster}
        elif preset in {'ally_one', 'ally_all'}:
            include = select(CharacterTags(
                camp=camp,
                alive=True,
                in_play=True
            ).export_tags())
            if preset == 'ally_one':
                return 1, include
            elif preset == 'ally_all':
                return len(include), include
        elif preset in {'enemy_one', 'enemy_all'}:
            include = select(CharacterTags(
                alive=True,
                in_play=True
            ).export_tags())
            exclude = select(CharacterTags(
                camp=camp,
            ).export_tags())
            if preset == 'enemy_one':
                return 1, include - exclude
            elif preset == 'enemy_all':
                return len(include - exclude), include - exclude

        raise ValueError('无效的条件')

    def selector_parse(
            self,
            caster: EntityID,
            selectors: list[SelectorT],
    ) -> list[tuple[int, set[CharacterID]]]:
        return list([self.character_selector(caster, preset) for preset in selectors])

    def add_status_pre(
            self,
            source: EntityID,
            target: CharacterID,
            status: Status,
    ) -> bool:
        """返回是否正式生效"""
        # ---------- 告知状态 ----------
        arg_could_add_status = signals.ArgCouldAddStatus(
            effective=True,
            source=source,
            target=target,
            status=status,
        )
        self.emit(self.signals.could_add_status, arg_could_add_status)
        # ---------- 生效 ----------
        if not arg_could_add_status.effective:
            return False
        arg_pre_add_status = signals.ArgPreAddStatus(
            source=source,
            target=target,
            status=status,
        )
        self.emit(self.signals.pre_add_status, arg_pre_add_status)
        return True

    def health(
            self,
            source: EntityID,
            target: CharacterID,
            value: int
    ) -> int:
        arg = signals.ArgHealth(
            source=source,
            target=target,
            value=value,
        )
        self.emit(self.signals.health, arg)
        return self.attributes.characters.modify_hp(arg.value, target)

    def add_status(
            self,
            status: Status,
            source: EntityID,
            target: CharacterID,
            slots: list[Slot[Any]],
            ready: Optional[Callable[[], None]] = None,
    ):
        """
        注册状态流程如下：

        1. 发起注册允许告知，收集是否允许（发射 Status）
           -- 失败返回 False
        2. 注册前告知（发射 Status）
        3. Status 及相关关系注册到 gs
        4. 收集 Status 状态依赖 Slot，RemoveStatus 绑定 deactivate 信号（依赖 check=status）
        5. 注册后生效前就绪 ready()
        6. 正式生效信号（传递 StatusID，因为已经在游戏系统中，成为活动属性）
           -- 返回 True

        :param status: Status 实例（静态属性）
        :param source: 伤害来源（最终是玩家/角色）
        :param target: 影响目标，为保证独立性，多目标自行多次添加
        :param slots: 伴随状态取消的事件订阅（槽）
        :param ready: 正式生效信号前的就绪函数
        """
        if not self.add_status_pre(source, target, status):
            return False

        statusid = self.register_status(status, target)

        def _check(arg_remove_status: signals.ArgRemoveStatus):
            return arg_remove_status.status.uuid == status.uuid

        def _remove(_: signals.ArgRemoveStatus):
            for slot in slots:
                slot.deactivate()

        self.signal_bus.connect(
            signal=self.signals.remove_status,
            check=_check,
            callback=_remove,
            times=1,
        )

        if ready:
            ready()

        arg_add_status = signals.ArgAddStatus(
            source=source,
            target=target,
            status=statusid,
        )
        self.emit(self.signals.add_status, arg_add_status)

        return True

    def remove_status(
            self,
            status: StatusID,
            source: EntityID,
    ):
        arg_pre_remove_status = signals.ArgPreRemoveStatus(
            effective=True,
            source=source,
            status=status,
        )
        self.emit(self.signals.pre_remove_status, arg_pre_remove_status)
        if not arg_pre_remove_status.effective:
            return False
        arg_remove_status = signals.ArgRemoveStatus(
            source=source,
            status=status,
        )
        self.emit(self.signals.remove_status, arg_remove_status)
        self.delete_status(status)
        return True

    def skill_usable(self, skill: SkillID) -> bool:
        character = self.relations.skills.get_parent(skill)

        if not self.attributes.characters.in_play.request(character):
            return False

        if not self.attributes.characters.alive.request(character):
            return False

        if not self.attributes.skills.usable.request(skill):
            return False

        return True

    def get_allowed_skills(self):
        """单独拉取技能是否允许使用"""
        res: dict[int, dict[int, dict[int, bool]]] = {}
        players = self.relations.players.get_all_items()
        for player in players:
            res[player.uuid] = {}
            rp = res[player.uuid]
            characters = self.relations.characters.get_children(player)
            for character in characters:
                rp[character.uuid] = {}
                rc = rp[character.uuid]
                for skill in self.relations.skills.get_children(character):
                    rc[skill.uuid] = self.skill_usable(skill)
        return res

    def turn_start(self):
        self.emit(self.signals.pre_turn_start, None)
        self.emit(self.signals.turn_start, None)

    def process(self):
        self.emit(self.signals.pre_turn_end, None)
        self.signal_bus.process()
        self.emit(self.signals.turn_end, None)

    def clean_up(self):
        self.relations.clean_up()
        self.tags.clean_up()
        self.signal_bus.clean_up()

    def clear(self):
        self.relations.clear()
        self.tags.clear()
        self.signal_bus.clear()
        temp = UUID()
        temp.uuid = 0

    def export_dict(self):
        res = []
        attr = self.attributes
        for player in self.relations.players.get_all_items():
            pr = attr.players.export_current(player).model_dump(
                include={'uuid', 'name', 'display_name'}
            )
            res.append(pr)
            pr['characters'] = []
            for character in self.relations.characters.get_children(player):
                pc = attr.characters.export_current(character).model_dump(
                    include={'uuid', 'name', 'display_name', 'hp', 'attack', 'defense', 'max_hp'}
                )
                pr['characters'].append(pc)
                pc['skills'] = []
                for skill in self.relations.skills.get_children(character):
                    pc['skills'].append(attr.skills.export_current(skill).model_dump(
                        include={'uuid', 'name', 'display_name', 'useable'})
                    )
        return res
