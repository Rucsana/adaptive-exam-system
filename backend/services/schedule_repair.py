from backend.models.assignment import Assignment
from backend.models.room import Room
from backend.models.invigilator import Invigilator
from backend.models.exam import Exam


class ScheduleRepair:

    def repair(
        self,
        exams: list[Exam],
        rooms: list[Room],
        invigilators: list[Invigilator],
        assignments: list[Assignment],
    ) -> list[Assignment]:

        exam_map = {
            exam.exam_id: exam
            for exam in exams
        }

        used_room_slots = set()
        used_invigilator_slots = set()
        student_slots = set()

        repaired = []

        possible_slots = sorted({
            slot
            for room in rooms
            for slot in room.available_slots
        })

        for assignment in assignments:

            exam = exam_map[assignment.exam_id]

            selected_slot = None
            selected_room = None
            selected_invigilator = None

            # =================================================
            # FIND VALID SLOT
            # =================================================

            for slot in possible_slots:

                students_available = True

                for student_id in exam.students:

                    if (student_id, slot) in student_slots:
                        students_available = False
                        break

                if not students_available:
                    continue

                # =================================================
                # FIND VALID ROOM
                # =================================================

                for room in rooms:

                    if room.capacity < len(exam.students):
                        continue

                    if slot not in room.available_slots:
                        continue

                    if (room.room_id, slot) in used_room_slots:
                        continue

                    selected_room = room
                    break

                if selected_room is None:
                    continue

                # =================================================
                # FIND ACTUALLY AVAILABLE INVIGILATOR
                # =================================================

                for invigilator in invigilators:

                    # Faculty must be free according to timetable
                    if slot not in invigilator.available_slots:
                        continue

                    # Faculty must have confirmed availability
                    if slot not in invigilator.confirmed_slots:
                        continue

                    # Faculty must have checked in
                    if slot not in invigilator.checked_in_slots:
                        continue

                    # Faculty cannot already be assigned
                    if (
                        invigilator.invigilator_id,
                        slot
                    ) in used_invigilator_slots:
                        continue

                    selected_invigilator = invigilator
                    break

                if selected_invigilator is None:
                    selected_room = None
                    continue

                selected_slot = slot
                break

            # =================================================
            # CREATE REPAIRED ASSIGNMENT
            # =================================================

            if (
                selected_slot
                and selected_room
                and selected_invigilator
            ):

                new_assignment = Assignment(
                    exam_id=assignment.exam_id,
                    slot_id=selected_slot,
                    room_id=selected_room.room_id,
                    invigilator_ids=[
                        selected_invigilator.invigilator_id
                    ],
                )

                repaired.append(new_assignment)

                used_room_slots.add(
                    (
                        selected_room.room_id,
                        selected_slot
                    )
                )

                used_invigilator_slots.add(
                    (
                        selected_invigilator.invigilator_id,
                        selected_slot
                    )
                )

                for student_id in exam.students:

                    student_slots.add(
                        (
                            student_id,
                            selected_slot
                        )
                    )

            else:

                raise ValueError(
                    f"Could not repair exam {assignment.exam_id}: "
                    "no valid slot, room, and confirmed/check-in "
                    "invigilator combination found."
                )

        return repaired