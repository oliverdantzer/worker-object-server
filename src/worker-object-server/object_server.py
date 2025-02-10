from __future__ import annotations
from typing import Any
import common
from typing import Union
from update_server import ConnectorServer
import time

Indexable = Union[dict, list]

class Object:
    position: common.Position
    # x.y.z
    # x[y][z]
    def __init__(self, db_api: DbApi, position: common.Position):
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
        self.db_api.add_update(common.Update(time.time(), self.position + name, value))

class DbApi:
    def __init__(self, server: ConnectorServer):
        self.server = server
        self.root = Object(db_api=self, position=common.Position())
    
    def get_value(self, position: common.Position) -> Any:
        return self.server.get_value(position)
    
    def add_update(self, update: common.Update) -> None:
        self.server.add_update(update)
    
    def __getitem__(self, name: str) -> Any:
        return self.root[name]
    
    def __setitem__(self, name: str, value: Any) -> None:
        self.root[name] = value