from pydantic import BaseModel
from typing import List


class Invigilator(BaseModel):
    invigilator_id: str
    name: str
    department: str

    # Timetable-based availability
    available_slots: List[str]

    # Faculty confirmation for assigned duties
    confirmed_slots: List[str] = []

    # Physical/current availability
    checked_in_slots: List[str] = []

    # Existing assignments
    assigned_slots: List[str] = []

    # Notifications sent to faculty
    notifications: List[str] = []

    block: str
    password: str = "faculty123"

    # Daily Teaching & Lecture Schedule (e.g. {"T1": "Free (No Lecture)", "T2": "Busy (CS302 Lecture)"})
    teaching_schedule: dict[str, str] = {}
