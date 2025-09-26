from typing import Callable

from ..common import singleton
from ..entity import (
    CharacterID,
    EntityID,
    Container,
    Effect,
    effect_export_config_schema,
)
from ..entity.container import NameT, export_character_fields
from ..gamesys import GameSys

gs = GameSys()


@singleton
class EffectSys:
    def __init__(self):
        self._names: set[str] = set()
        self._descriptions: dict[str, str] = {}
        self._effects: dict[str, type[Effect]] = {}

        self.casters: dict[EntityID, EntityID] = {}
        self.containers: dict[EntityID, Container] = {}

    def register(
            self,
            name: str,
            description: str,
    ) -> Callable[[type[Effect]], type[Effect]]:
        """注册效果"""
        if name in self._names:
            raise RuntimeError(f"effect {name} already registered")

        def decorator(cls: type[Effect]) -> type[Effect]:
            self._names.add(name)
            self._descriptions[name] = description
            self._effects[name] = cls
            return cls

        return decorator

    def load_container(
            self,
            caster: EntityID,
            belong: EntityID,
            container: Container,
    ):
        # 注意，container 的 uuid 与存载实体(归属)一致
        effects: list[Effect] = []

        selectors_len: int = len(container.selectors)
        effect_name: list[NameT] = container.exoprt_effect_name()

        for name, effect_config in zip(effect_name, container.effect_config):
            effect_schema = self._effects[name]
            effect_config_schema = effect_export_config_schema(name, effect_schema, selectors_len)
            effect_config_schema.model_validate(effect_config)

            character_fields = export_character_fields(effect_schema)
            effect_fields = effect_config | {character: None for character in character_fields}
            effects.append(effect_schema(**effect_fields))

        container.effects = effects
        self.casters[belong] = caster
        self.containers[belong] = container

    def export_container_need(self, belong: EntityID):
        if belong not in self.containers:
            raise RuntimeError(f"container {belong} not loaded")

        return gs.selector_parse(
            caster=self.casters[belong],
            selectors=self.containers[belong].selectors,
        )

    def run_container(self, belong: EntityID, selections: list[list[CharacterID]]):
        if belong not in self.containers:
            raise RuntimeError(f"Container {belong} not loaded")

        container = self.containers[belong]
        for effect, config in zip(container.effects, container.effect_config):
            character_fields = export_character_fields(type(effect))
            for field in character_fields:
                index = config[field]
                setattr(effect, field, selections[index])
        # 无依赖，延迟执行保证不交叉
        container.run()

    def clear(self):
        for container in self.containers.values():
            container.clear()

        self.casters.clear()
        self.containers.clear()
