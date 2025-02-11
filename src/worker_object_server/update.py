from __future__ import annotations
import json
from typing import Union, Any, Dict, List
from datetime import datetime
from pydantic import BaseModel


class JsonObj(BaseModel):
    __root__: Union[
        Dict[str, 'JsonObj'],
        List['JsonObj'],
        str,
        int,
        float,
        bool,
        None
    ]


class JsonIterable(BaseModel):
    __root__: Union[List[JsonObj], Dict[str, JsonObj]]


class Position(BaseModel):
    __root__: List[str]

    def __init__(self, position: List[str] = []):
        super().__init__(__root__=position or [])

    # string representation for debugging
    def __repr__(self):
        return ".".join(self.__root__)

    def __add__(self, other: str):
        return Position(self.__root__ + [other])

    @staticmethod
    def from_str(string: str) -> 'Position':
        position = string.split(".")
        return Position(position)

    def serialize(self):
        return self.__root__.copy()


class Update(BaseModel):
    timestamp: datetime
    position: Position
    data: Any


class UpdatePacket(BaseModel):
    timestamp: datetime
    position: List[str]
    data: JsonObj

    @staticmethod
    def from_update(update: Update) -> UpdatePacket:
        return UpdatePacket(
            timestamp=update.timestamp,
            position=update.position.serialize(),
            data=JsonObj(__root__=update.data)
        )

    @staticmethod
    def from_json_str(string: str) -> UpdatePacket:
        obj = json.loads(string)
        return UpdatePacket(**obj)

    def json(self):
        return json.dumps({
            "timestamp": self.timestamp,
            "position": self.position,
            "data": self.data
        })


def update_dict(data: dict, update: UpdatePacket):
    current = data
    for key in update.position:
        current = current[key]
    current[update.position[-1]] = update.data
