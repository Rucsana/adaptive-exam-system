from pydantic import BaseModel
from typing import List


class Exam(BaseModel):
    exam_id: str
    subject: str
    duration: int
    students: List[str]
    preferred_slots: List[str] = []
    special_requirements: List[str] = []