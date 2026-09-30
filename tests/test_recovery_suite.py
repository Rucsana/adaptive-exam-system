import unittest
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.models.student import Student
from backend.models.exam import Exam
from backend.models.room import Room
from backend.models.invigilator import Invigilator
from backend.services.disruption_service import DisruptionService
from backend.agents.exam_scheduler_agent import ExamSchedulerAgent


class TestExamRecoverySuite(unittest.TestCase):

    def setUp(self):
        self.students = [
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

        self.exams = [
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

        self.rooms = [
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

        self.invigilators = [
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

        self.agent = ExamSchedulerAgent()
        self.disruption_service = DisruptionService()

    def test_01_initial_plan_and_validation(self):
        """Initial schedule planning must create a valid schedule matching EX01->T1, EX02->T2."""
        schedule = self.agent.plan_schedule(self.exams, self.rooms, self.invigilators)
        self.assertEqual(len(schedule), 2)

        errors = self.agent.validate_schedule(
            self.students, self.exams, self.rooms, self.invigilators, schedule
        )
        self.assertEqual(errors, [], "Initial schedule should have 0 validation errors.")

        assignment_map = {a.exam_id: a for a in schedule}
        self.assertEqual(assignment_map["EX01"].slot_id, "T1")
        self.assertEqual(assignment_map["EX01"].room_id, "R102")
        self.assertIn("I02", assignment_map["EX01"].invigilator_ids)

        self.assertEqual(assignment_map["EX02"].slot_id, "T2")
        self.assertEqual(assignment_map["EX02"].room_id, "R102")
        self.assertIn("I01", assignment_map["EX02"].invigilator_ids)

    def test_02_room_disruption_recovery(self):
        """Room R102 becomes unavailable in T1; agent relocates EX01 to R103 with I02 and preserves EX02."""
        recovered = self.agent.run_recovery_cycle(
            students=self.students,
            exams=self.exams,
            rooms=self.rooms,
            invigilators=self.invigilators,
            disruption_service=self.disruption_service,
            disruption_type="room",
            disrupted_room_id="R102",
            disrupted_slot_id="T1",
        )

        res_map = {a.exam_id: a for a in recovered}
        self.assertEqual(res_map["EX01"].room_id, "R103")
        self.assertEqual(res_map["EX01"].slot_id, "T1")
        self.assertIn("I02", res_map["EX01"].invigilator_ids)

        # Unaffected assignment must be preserved
        self.assertEqual(res_map["EX02"].room_id, "R102")
        self.assertEqual(res_map["EX02"].slot_id, "T2")
        self.assertIn("I01", res_map["EX02"].invigilator_ids)

    def test_03_invigilator_disruption_recovery(self):
        """Invigilator I02 becomes unavailable in T1; agent reassigns EX01 to I03 and preserves EX02."""
        recovered = self.agent.run_recovery_cycle(
            students=self.students,
            exams=self.exams,
            rooms=self.rooms,
            invigilators=self.invigilators,
            disruption_service=self.disruption_service,
            disruption_type="invigilator",
            disrupted_invigilator_id="I02",
            disrupted_slot_id="T1",
        )

        res_map = {a.exam_id: a for a in recovered}
        self.assertEqual(res_map["EX01"].room_id, "R102")
        self.assertEqual(res_map["EX01"].slot_id, "T1")
        self.assertIn("I03", res_map["EX01"].invigilator_ids)

        # Unaffected assignment must be preserved
        self.assertEqual(res_map["EX02"].room_id, "R102")
        self.assertEqual(res_map["EX02"].slot_id, "T2")
        self.assertIn("I01", res_map["EX02"].invigilator_ids)

        # Notifications check
        i02 = next(inv for inv in self.invigilators if inv.invigilator_id == "I02")
        i03 = next(inv for inv in self.invigilators if inv.invigilator_id == "I03")
        self.assertTrue(any("Duty Relieved" in n for n in i02.notifications))
        self.assertTrue(any("reassigned from I02 to I03" in n for n in i03.notifications))

    def test_04_compound_disruption_recovery(self):
        """Both room R102 and invigilator I02 unavailable in T1; agent repairs both to R103 and I03."""
        recovered = self.agent.run_recovery_cycle(
            students=self.students,
            exams=self.exams,
            rooms=self.rooms,
            invigilators=self.invigilators,
            disruption_service=self.disruption_service,
            disruption_type="compound",
            disrupted_room_id="R102",
            disrupted_invigilator_id="I02",
            disrupted_slot_id="T1",
        )

        res_map = {a.exam_id: a for a in recovered}
        self.assertEqual(res_map["EX01"].room_id, "R103")
        self.assertEqual(res_map["EX01"].slot_id, "T1")
        self.assertIn("I03", res_map["EX01"].invigilator_ids)

        # Unaffected assignment must be preserved
        self.assertEqual(res_map["EX02"].room_id, "R102")
        self.assertEqual(res_map["EX02"].slot_id, "T2")
        self.assertIn("I01", res_map["EX02"].invigilator_ids)

    def test_05_explicit_failure_when_no_valid_backup(self):
        """When backup faculty I03 is unconfirmed or not checked in, recovery must explicitly fail."""
        # Make I03 unconfirmed
        self.invigilators[2].confirmed_slots = []
        self.invigilators[2].checked_in_slots = []

        with self.assertRaises(ValueError) as ctx:
            self.agent.run_recovery_cycle(
                students=self.students,
                exams=self.exams,
                rooms=self.rooms,
                invigilators=self.invigilators,
                disruption_service=self.disruption_service,
                disruption_type="invigilator",
                disrupted_invigilator_id="I02",
                disrupted_slot_id="T1",
            )

        self.assertIn("no valid slot, room, and confirmed/check-in", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
