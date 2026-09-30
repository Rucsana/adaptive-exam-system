from pydantic import BaseModel


class TimeSlot(BaseModel):
    slot_id: str
    date: str
    start_time: str
    end_time: str