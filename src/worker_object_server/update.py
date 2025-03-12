from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import BaseModel, RootModel, ValidationError

type Jsonable = Union[Dict[str, "Jsonable"],
                      List["Jsonable"], str, int, float, bool, None]


class JsonData(RootModel):
    root: Union[Dict[str, "JsonData"],
                List["JsonData"], str, int, float, bool, None]

    @staticmethod
    def from_data(data: Any) -> JsonData:
        try:
            return JsonData(data)
        except ValidationError:
            if data.__class__ == Union[Dict[str, "JsonData"], List["JsonData"]]:
                acc = []
                for item in data:
                    try:
                        acc.append(JsonData.from_data(item))
                    except ValidationError:
                        pass
                return JsonData(acc)
            else:
                raise ValueError("Root of obj is not prunable to JSON type")

    @staticmethod
    def parse(data: Any) -> Jsonable:
        json_data = JsonData.from_data(data)
        return json.loads(json_data.stringify())

    def stringify(self):
        return json.dumps(self.root, cls=JsonValEncoder)


class JsonValEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonData):
            return obj.root
        return super().default(obj)


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
    data: Jsonable


class UpdatePacket(BaseModel):
    timestamp: datetime
    position: List[str]
    data: Jsonable

    @staticmethod
    def from_update(update: Update) -> UpdatePacket:
        return UpdatePacket(
            timestamp=update.timestamp,
            position=update.position.serialize(),
            data=update.data,
        )

    def to_update(self) -> Update:
        return Update(
            timestamp=self.timestamp,
            position=Position(self.position),
            data=self.data,
        )

    def json(self):
        try:
            return json.dumps(
                {
                    "timestamp": self.timestamp.isoformat(),  # Convert datetime to string
                    "position": self.position,
                    "data": self.data,  # Convert JsonVal to serializable format
                }
            )
        except Exception as e:
            print("data", self.data)
            print("err", e)
            raise ValueError("Error in converting UpdatePacket to JSON")


def update_obj(obj: dict, update: UpdatePacket):
    current = obj
    for key in update.position:
        current = current[key]
    current[update.position[-1]] = update.data
