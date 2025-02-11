from __future__ import annotations

from datetime import datetime
from typing import Any, Union

from .update import Position, Update, UpdatePacket
from .update_server import UpdateServer

Indexable = Union[dict, list]


class Object:
    position: Position

    def __init__(self, object_server: ObjectServer, position: Position):
        self.position = position
        self.object_server = object_server

    def __getitem__(self, name: str) -> Any:
        value = self.object_server.get_at_position(self.position + name)
        if value is Indexable:
            return Object(self.object_server, self.position + name)
        else:
            return value

    def __setitem__(self, name: str, value: Any) -> None:
        value = self.object_server.get_at_position(self.position + name)
        position = self.position + name
        update = Update(timestamp=datetime.now(), position=position, data=value)
        self.object_server.add_update(update)


class ObjectServer:
    def __init__(self, data = {}):
        self.data = data
        self.server = UpdateServer(
            get_at_position=self.get_at_position,
            handle_incoming_update=self.handle_incoming_update,
        )
        self.root = Object(object_server=self, position=Position([]))

    def __repr__(self):
        return self.data.__repr__()

    def get_at_position(self, position: Position) -> Any:
        current = self.data
        for key in position:
            current = current[key]
        return current

    def handle_incoming_update(self, update: UpdatePacket):
        current = self.data
        for key in update.position[:-1]:
            current = current[key]
        current[-1] = update.data

    def set_at_position(self, position: Position) -> Any:
        return self.server.get_at_position(position)

    def add_update(self, update: Update) -> None:
        self.server.add_update(update)

    def __getitem__(self, name: str) -> Any:
        return self.root[name]

    def __setitem__(self, name: str, value: Any) -> None:
        self.root[name] = value
