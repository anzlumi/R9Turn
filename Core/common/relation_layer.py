"""
层级模块功能说明：

针对情况：子节点必定有父节点，父节点必定有子节点（否则自动删除）

抽象：RelationLayer, Relations


RelationLayer 功能：

> 针对一层的父子节点管理，父节点不会成为子节点，子节点不会成为父节点

1. 添加子-父节点管理关系

2. 删除子节点，若父节点为空，自动删除父节点

3. 删除父节点，同时删除其所有子节点

4. 获得子节点的父节点，获得父节点的所有子节点

5. 获得全部存在的父节点，获得全部存在的子节点

Relations 功能：

> 维护 RelationLayer，提供统一接口
"""

from typing import TypeVar, Generic, Hashable, Dict, Set, Optional

ItemT = TypeVar('ItemT', bound=Hashable)
ParentT = TypeVar('ParentT', bound=Hashable)


class RelationLayer(Generic[ItemT, ParentT]):
    """
    关系层级管理器，侧重点是子节点
    """

    def __init__(self) -> None:
        self._item_to_parent: Dict[ItemT, ParentT] = {}
        self._parent_to_items: Dict[ParentT, Set[ItemT]] = {}

    def add(self, item: ItemT, parent: ParentT) -> None:
        """添加关系：item 属于 parent"""
        if item in self._item_to_parent:
            raise ValueError(f"Item {item} already exists")

        self._item_to_parent[item] = parent
        self._parent_to_items.setdefault(parent, set()).add(item)

    def remove_item(self, item: ItemT) -> None:
        """移除子节点及其关系"""
        if item not in self._item_to_parent:
            return

        parent = self._item_to_parent.pop(item)
        items = self._parent_to_items[parent]
        items.remove(item)

        if not items:
            self._parent_to_items.pop(parent)

    def remove_parent(self, parent: ParentT) -> None:
        """移除父节点及其所有子节点"""
        if parent not in self._parent_to_items:
            return

        items = self._parent_to_items.pop(parent)
        for item in items:
            self._item_to_parent.pop(item)

    def get_parent(self, item: ItemT) -> Optional[ParentT]:
        """获取子节点的父节点"""
        return self._item_to_parent.get(item)

    def get_children(self, parent: ParentT) -> Set[ItemT]:
        """获取父节点的所有子节点"""
        return self._parent_to_items.get(parent, set())

    def has_item(self, item: ItemT) -> bool:
        """检查子节点是否存在"""
        return item in self._item_to_parent

    def update(self, item: ItemT, new_parent: ParentT) -> None:
        """修改子节点的父节点"""
        # 如果item已有父节点，先移除旧关系
        if item in self._item_to_parent:
            self.remove_item(item)

        self.add(item, new_parent)

    def clear(self) -> None:
        """清空所有关系"""
        self._item_to_parent.clear()
        self._parent_to_items.clear()

    def get_all_items(self) -> set[ItemT]:
        """获取所有子节点"""
        return set(self._item_to_parent.keys())

    def get_item_list(self) -> list[ItemT]:
        return list(self._item_to_parent.keys())

    def get_all_parents(self) -> set[ParentT]:
        """获取所有父节点"""
        return set(self._parent_to_items.keys())
