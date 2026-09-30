from backend.models.student import Student
from backend.models.exam import Exam
from backend.models.room import Room
from backend.models.invigilator import Invigilator

from backend.services.disruption_service import DisruptionService
from backend.agents.exam_scheduler_agent import ExamSchedulerAgent


# ============================================================
# TEST DATA
# ============================================================

students = [
    Student(
        student_id="S101",
        name="Alice",
        department="CSE",
        year=3,
        block="A",
        accessibility_requirement="ground_floor_required",
    ),
    Student(
        student_id="S102",
        name="Bob",
        department="CSE",
        year=3,
        block="A",
    ),
]


exams = [
    Exam(
        exam_id="EX01",
        subject="Data Structures",
        duration=3,
        students=["S101", "S102"],
    ),
    Exam(
        exam_id="EX02",
        subject="Database Management",
        duration=3,
        students=["S101", "S102"],
    ),
]


rooms = [
    Room(
        room_id="R101",
        building="A",
        floor=1,
        capacity=1,
        available_slots=["T2"],
        accessibility_features=[],
    ),
    Room(
        room_id="R102",
        building="A",
        floor=1,
        capacity=60,
        available_slots=["T1", "T2"],
        accessibility_features=["ground_floor_required"],
    ),
    Room(
        room_id="R103",
        building="B",
        floor=1,
        capacity=60,
        available_slots=["T1", "T2"],
        accessibility_features=["ground_floor_required"],
    ),
]


invigilators = [
    Invigilator(
        invigilator_id="I01",
        name="Dr. Test",
        department="CSE",
        available_slots=["T2"],
        confirmed_slots=["T2"],
        checked_in_slots=["T2"],
        block="A",
    ),
    Invigilator(
        invigilator_id="I02",
        name="Dr. Backup",
        department="ECE",
        available_slots=["T1", "T2"],
        confirmed_slots=["T1", "T2"],
        checked_in_slots=["T1", "T2"],
        block="A",
    ),
    Invigilator(
        invigilator_id="I03",
        name="Dr. Emergency Backup",
        department="IT",
        available_slots=["T1", "T2"],
        confirmed_slots=["T1", "T2"],
        checked_in_slots=["T1", "T2"],
        block="B",
    ),
]


# ============================================================
# AUTONOMOUS RECOVERY DEMO SCRIPT
# ============================================================

if __name__ == "__main__":
    agent = ExamSchedulerAgent()
    disruption_service = DisruptionService()

    print("\n========================================")
    print("       🤖 AUTONOMOUS AGENT DEMO")
    print("========================================")

    final_schedule = agent.run_recovery_cycle(
        students=students,
        exams=exams,
        rooms=rooms,
        invigilators=invigilators,
        disruption_service=disruption_service,
        disrupted_room_id="R102",
        disrupted_slot_id="T1",
    )

    print("\n========================================")
    print("          🤖 FINAL RESULT")
    print("========================================")

    if final_schedule:
        print("✅ AGENT SUCCESSFULLY RECOVERED SCHEDULE\n")
        for assignment in final_schedule:
            print(
                f"{assignment.exam_id} → "
                f"{assignment.slot_id} → "
                f"{assignment.room_id} → "
                f"{assignment.invigilator_ids}"
            )
    else:
        print("❌ AGENT FAILED TO RECOVER SCHEDULE")