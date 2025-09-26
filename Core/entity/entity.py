from typing import Optional, TypeAlias, Any, Callable

from pydantic import BaseModel
from pydantic_core import core_schema

TagCombT: TypeAlias = list[set[tuple[str, str]]]


class Entity(BaseModel):
    model_config = {'extra': 'forbid'}

    uuid: int = 0
    """uuid 实例唯一标识符，数字"""
    camp: int = 0
    """阵营，须有游戏管理器统一管理"""
    name: Optional[str] = None
    """name 类唯一可读标识符"""
    display_name: Optional[str] = None
    """display name 显示名，可中文"""
    description: Optional[str] = None
    """description 描述"""

    def ready(self) -> None:
        pass

    def process(self):
        pass

    def clear(self) -> None:
        pass

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Entity):
            return self.uuid == other.uuid
        return NotImplemented

    def __repr__(self) -> str:
        return f'Entity {self.uuid} {self.name} {self.display_name}'


class EntityID:
    def __init__(self, uuid: int):
        self.uuid: int = uuid

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EntityID):
            return self.uuid == other.uuid
        raise NotImplemented

    def __repr__(self) -> str:
        return f'EntityID {self.uuid}'

    @classmethod
    def validate(cls, value: "int | EntityID") -> "EntityID":
        """接受整数或已有的 EntityID 实例"""
        if isinstance(value, EntityID):
            return value  # 直接返回已有实例
        if not isinstance(value, int):
            raise ValueError(f"EntityID 必须为整数或EntityID实例，收到 {type(value)}")
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            source_type: Any,
            handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.int_schema(),
                core_schema.is_instance_schema(cls),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.uuid,
                return_schema=core_schema.int_schema(),
            ),
        )

    # 添加 JSON 序列化支持
    def __json__(self) -> int:
        return self.uuid


def make_tags(tags: dict[str, set[str]]) -> TagCombT:
    return [set((key, str(value)) for value in values) for key, values in tags.items()]


class EntityTags(BaseModel):
    uuid: Optional[set[int] | int] = None
    camp: Optional[set[int] | int] = None

    model_config = {'extra': 'ignore'}

    def export_tags(self) -> TagCombT:
        res: dict[str, set[str]] = {}
        for key, values in self.model_dump(exclude_none=True).items():
            if not isinstance(values, set):
                res[key] = {str(values)}
            else:
                res[key] = {str(value) for value in values}
        return make_tags(res)
