from typing import Generic, TypeVar, Hashable

ItemT = TypeVar('ItemT', bound=Hashable)
TagT = TypeVar('TagT', bound=Hashable)


class TagsManager(Generic[ItemT, TagT]):
    def __init__(self) -> None:
        """标签搜索库"""
        self.item_to_tags: dict[ItemT, set[TagT]] = {}
        self.tag_to_items: dict[TagT, set[ItemT]] = {}

    def add(self, item: ItemT, tags: set[TagT]) -> None:
        """添加 item 极其对应标签，标签不应空，不会删除旧标签，添加推荐使用 update"""
        if not tags:
            raise ValueError('Tags cannot be empty.')

        if item not in self.item_to_tags:
            self.item_to_tags[item] = set()

        for tag in tags:
            if tag not in self.tag_to_items:
                self.tag_to_items[tag] = set()

            self.tag_to_items[tag].add(item)
            self.item_to_tags[item].add(tag)

    def remove_item(self, item: ItemT) -> None:
        """
        删除 item 及其所有标签 \n
        允许重复删除不报错
        """
        if item not in self.item_to_tags:
            return

        tags = self.item_to_tags.pop(item)

        for tag in tags:
            self.tag_to_items[tag].discard(item)

            # 清理空集
            if not self.tag_to_items[tag]:
                del self.tag_to_items[tag]

    def update(self, item: ItemT, tags: set[TagT]) -> None:
        """更新标签，不存在则添加"""
        if item in self.item_to_tags:
            self.remove_item(item)

        self.add(item, tags)

    def select_and(self, tags: set[TagT]) -> set[ItemT]:
        """搜索标签对应的 item，遵循单调性，空 set 表示选择所有"""
        if not tags:
            return set(self.item_to_tags)

        list_to_and = [self.tag_to_items.get(tag, set()) for tag in tags]
        return set.intersection(*list_to_and)

    def select_or(self, tags: set[TagT]) -> set[ItemT]:
        """搜索标签对应的 item，遵循单调性，空 set 表示不选择"""
        if not tags:
            return set()

        list_to_or = [self.tag_to_items.get(tag, set()) for tag in tags]
        return set.union(*list_to_or)

    def select(self, tags_group: list[set[TagT]]) -> set[ItemT]:
        """形式是一系列标签集，标签集内部取并，最终取交"""
        # 同样单调，[] 返回全部
        if len(tags_group) == 0:
            return set(self.item_to_tags)

        list_to_and = [self.select_or(tags) for tags in tags_group]
        return set.intersection(*list_to_and)

    def select_and_inexclude(self, include: set[TagT], exclude: set[TagT]) -> set[ItemT]:
        """
        等价于 TagsManager.select_and(include) - TagsManager.select_and(exclude) \n
        注意，这并不是 TagsManager.select_and(include - exclude)
        """
        if include <= exclude or not exclude:
            return set()
        return self.select_and(include) - self.select_and(exclude)

    def clean_up(self) -> None:
        """
        正常使用 add、remove，同时外部不直接操作内部字典，则 clean_up 实际不会工作
        """
        for item in list(self.item_to_tags):
            if not self.item_to_tags[item]:
                del self.item_to_tags[item]

        for tag in list(self.tag_to_items):
            if not self.tag_to_items[tag]:
                del self.tag_to_items[tag]

    def clear(self) -> None:
        self.item_to_tags.clear()
        self.tag_to_items.clear()
