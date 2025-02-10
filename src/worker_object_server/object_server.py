from __future__ import annotations
from typing import Any
from .update import Position, Update
from typing import Union
from .update_server import UpdateServer
from datetime import datetime
import time

Indexable = Union[dict, list]


class Object:
    position: Position
    # x.y.z
    # x[y][z]

    def __init__(self, db_api: ObjectServer, position: Position):
        self.position = position
        self.db_api = db_api

    def __getitem__(self, name: str) -> Any:
        value = self.db_api.get_value(self.position + name)
        if value is Indexable:
            return Object(self.db_api, self.position + name)
        else:
            return value

    def __setitem__(self, name: str, value: Any) -> None:
        value = self.db_api.get_value(self.position + name)
        position = self.position + name
        update = Update(
            timestamp=datetime.now(), position=position, data=value)
        self.db_api.add_update(update)


class ObjectServer:
    def __init__(self, server: UpdateServer):
        self.server = server
        self.root = Object(db_api=self, position=Position())

    def get_value(self, position: Position) -> Any:
        return self.server.get_value(position)

    def add_update(self, update: Update) -> None:
        self.server.add_update(update)

    def __getitem__(self, name: str) -> Any:
        return self.root[name]

    def __setitem__(self, name: str, value: Any) -> None:
        self.root[name] = value
