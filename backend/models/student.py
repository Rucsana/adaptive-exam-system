from pydantic import BaseModel


class Student(BaseModel):
    student_id: str
    name: str
    department: str
    year: int
    block: str
    accessibility_requirement: str | None = None