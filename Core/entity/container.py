from typing import Literal, TypeAlias, Any, Optional

from pydantic import BaseModel, create_model, Field

from .character import CharacterID
from .entity import Entity, EntityTags, EntityID

SelectorT: TypeAlias = Literal[
    'caster',
    'ally_one',
    'ally_all',
    'enemy_one',
    'enemy_all',
]
NameT: TypeAlias = str
NumT: TypeAlias = int
CharacterT: TypeAlias = Optional[list[CharacterID]]
CharacterConfigT: TypeAlias = int


class Effect(BaseModel):
    def ready(self) -> None:
        pass

    def run(self) -> None:
        pass

    def clear(self) -> None:
        pass


def effect_export_config_schema(
        name: str,
        effect: type[Effect],
        selector_range: int
) -> type[BaseModel]:
    """
    针对一个 Effect 将其导出为特供配置文件的验证器
    """
    fields: dict[str, tuple[type, Any]] = {'name': (str, Field())}
    for field, info in effect.__pydantic_fields__.items():
        if info.annotation == CharacterT:
            fields[field] = (CharacterConfigT, Field(ge=0, lt=selector_range))
        else:
            fields[field] = (info.annotation, info)
    return create_model(name, **fields)


def export_character_fields(effect: type[Effect]) -> set[str]:
    """注册效果极其对应导出字段"""
    res = set()
    for field, info in effect.__pydantic_fields__.items():
        if info.annotation == CharacterT:
            res.add(field)
    return res


class Container(Entity):
    selectors: list[SelectorT]
    """选择器集"""
    effect_config: list[dict[str, Any]]
    """效果配置"""
    effects: list[Effect] = []
    """效果实例"""

    def ready(self):
        for effect in self.effects:
            effect.ready()

    def run(self):
        for effect in self.effects:
            effect.run()

    def exoprt_effect_name(self) -> list[str]:
        return [
            str(effect['name'])
            for effect in self.effect_config
        ]

    def clear(self) -> None:
        for effect in self.effects:
            effect.clear()


class ContainerTags(EntityTags):
    pass


class ContainerID(EntityID): pass
