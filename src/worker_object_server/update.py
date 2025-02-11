from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import BaseModel, RootModel

JsonObj = RootModel[
    Union[Dict[str, "JsonObj"], List["JsonObj"], str, int, float, bool, None]
]

JsonIterable = RootModel[Union[List[JsonObj], Dict[str, JsonObj]]]


class Position(RootModel):
    root: List[str]

    def __iter__(self):
        return iter(self.root)

    # string representation for debugging
    def __repr__(self):
        return ".".join(self.root)

    def __add__(self, other: str):
        return Position(self.root + [other])

    @staticmethod
    def from_str(string: str) -> "Position":
        position = string.split(".")
        return Position(position)

    def serialize(self):
        return self.root.copy()


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
            data=JsonObj.model_validate(update.data),
        )

    def json(self):
        return json.dumps(
            {"timestamp": self.timestamp, "position": self.position, "data": self.data}
        )


def update_dict(data: dict, update: UpdatePacket):
    current = data
    for key in update.position:
        current = current[key]
    current[update.position[-1]] = update.data
