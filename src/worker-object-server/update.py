from __future__ import annotations
from abc import ABC, abstractmethod
import json
from typing import Union, Any, Dict, List
import copy
from datetime import datetime
from pydantic import BaseModel, PositiveInt


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

    def __init__(self, position: list[str] = []):
        self.position = position.copy()

    def __repr__(self):
        return ".".join(self.position)

    def __add__(self, other: str):
        return Position(self.position + [other])

    @staticmethod
    def from_str(string: str) -> 'Position':
        position = string.split(".")
        return Position(position)

class Update(BaseModel):
    timestamp: datetime
    position: List[str]
    data: Any

class UpdatePacket(BaseModel, Update):
    timestamp: datetime
    position: List[str]
    data: JsonObj
    
    @staticmethod
    def from_update(update: Update) -> UpdatePacket:
        return UpdatePacket(**update)
    
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
