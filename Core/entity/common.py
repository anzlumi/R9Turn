"""

"""
from typing import TypeAlias

from .arm import Arm, ArmTags
from .card import Card, CardTags
from .character import Character, CharacterTags
from .container import Container, ContainerTags
from .entity import Entity, EntityTags
from .game import Game, GameTags
from .player import Player, PlayerTags
from .skill import Skill, SkillTags
from .status import Status, StatusTags

_entities_type: list[type[Entity]] = [
    Character,
    Player,
    Skill,
    Container,
    Status,
    Card,
    Arm,
    Game,
]

_entities_tags: list[type[EntityTags]] = [
    CharacterTags,
    PlayerTags,
    SkillTags,
    ContainerTags,
    StatusTags,
    CardTags,
    ArmTags,
    GameTags,
]

TagCombT: TypeAlias = list[set[tuple[str, str]]]


def export_tags(entity: Entity) -> TagCombT:
    for entity_type, entity_tags in zip(_entities_type, _entities_tags):
        if isinstance(entity, entity_type):
            return entity_tags(**entity.model_dump()).export_tags()

    raise TypeError('invalid entity type')


def export_flat_tags(entity: Entity) -> set[tuple[str, str]]:
    tags_comb: TagCombT = export_tags(entity)

    res: set[tuple[str, str]] = set()
    for field in tags_comb:
        for item in field:
            res.add(item)

    return res
