from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import BaseModel, RootModel, ValidationError


class JsonVal(RootModel):
    root: Union[Dict[str, "JsonVal"], List["JsonVal"], str, int, float, bool, None]

    @staticmethod
    def from_obj(obj: Any) -> JsonVal:
        try:
            return JsonVal(obj)
        except ValidationError:
            if obj.__class__ == Union[Dict[str, "JsonVal"], List["JsonVal"]]:
                acc = []
                for item in obj:
                    try:
                        acc.append(JsonVal.from_obj(item))
                    except ValidationError:
                        pass
                return JsonVal(acc)
            else:
                raise ValueError("Root of obj is not prunable to JSON type")


class Position(RootModel):
    root: List[str]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, index: Union[int, slice]):
        return self.root[index]

    # 0 is root position
    def depth(self):
        return len(self.root)

    # string representation for debugging
    def __str__(self):
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
    data: JsonVal

    @staticmethod
    def from_update(update: Update) -> UpdatePacket:
        return UpdatePacket(
            timestamp=update.timestamp,
            position=update.position.serialize(),
            data=JsonVal.from_obj(update.data),
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
