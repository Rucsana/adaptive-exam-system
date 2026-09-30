from pydantic import BaseModel
from typing import List


class Room(BaseModel):
    room_id: str
    building: str
    floor: int
    capacity: int
    available_slots: List[str]
    accessibility_features: List[str] = []