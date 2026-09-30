from pydantic import BaseModel
from typing import List


class Assignment(BaseModel):
    exam_id: str
    slot_id: str
    room_id: str
    invigilator_ids: List[str]