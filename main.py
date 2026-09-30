from backend.models.student import Student


student = Student(
    student_id="S101",
    name="Test Student",
    department="CSE",
    year=3,
    block="A",
    accessibility_requirement="ground_floor_required",
)

print(student)