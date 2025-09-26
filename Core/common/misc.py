import json
from typing import Any


def singleton(cls):
    """
    单例装饰器
    """
    _instance = {}

    def func(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return func


@singleton
class UUID:
    def __init__(self) -> None:
        self.uuid = 0

    def assign(self) -> int:
        self.uuid += 1
        return self.uuid

    def __call__(self) -> int:
        return self.assign()


def uuid() -> int:
    temp = UUID()
    return temp.assign()


def json_load(path: str) -> dict[str, Any]:
    with open(path, encoding='utf-8') as file:
        return json.loads(file.read())


def json_print(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))


def get_variable_name(variable):
    for name, value in locals().items():
        if value is variable:
            return name
    return None
