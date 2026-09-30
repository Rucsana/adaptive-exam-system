from backend.models.exam import Exam
from backend.models.room import Room
from backend.models.invigilator import Invigilator
from backend.models.assignment import Assignment


class SchedulePlanner:

    def plan(
        self,
        exams: list[Exam],
        rooms: list[Room],
        invigilators: list[Invigilator],
    ) -> list[Assignment]:

        assignments = []

        used_room_slots = set()
        used_invigilator_slots = set()
        student_slots = set()

        # Collect all available time slots
        possible_slots = sorted({
            slot
            for room in rooms
            for slot in room.available_slots
        })

        for exam in exams:

            assigned = False

            for slot in possible_slots:

                # -----------------------------------------
                # Check student conflicts
                # -----------------------------------------

                student_conflict = False

                for student_id in exam.students:
                    if (student_id, slot) in student_slots:
                        student_conflict = True
                        break

                if student_conflict:
                    continue

                # -----------------------------------------
                # Find a suitable room
                # -----------------------------------------

                selected_room = None

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

                # -----------------------------------------
                # Find an available invigilator
                # -----------------------------------------

                selected_invigilator = None

                for invigilator in invigilators:

                    if slot not in invigilator.available_slots:
                        continue

                    if slot not in invigilator.confirmed_slots:
                        continue

                    if slot not in invigilator.checked_in_slots:
                        continue

                    if (
                        invigilator.invigilator_id,
                        slot
                    ) in used_invigilator_slots:
                        continue

                    selected_invigilator = invigilator
                    break

                if selected_invigilator is None:
                    continue

                # -----------------------------------------
                # Create assignment
                # -----------------------------------------

                assignment = Assignment(
                    exam_id=exam.exam_id,
                    slot_id=slot,
                    room_id=selected_room.room_id,
                    invigilator_ids=[
                        selected_invigilator.invigilator_id
                    ],
                )

                assignments.append(assignment)

                # Record resource usage
                used_room_slots.add(
                    (
                        selected_room.room_id,
                        slot
                    )
                )

                used_invigilator_slots.add(
                    (
                        selected_invigilator.invigilator_id,
                        slot
                    )
                )

                # Record student usage
                for student_id in exam.students:
                    student_slots.add(
                        (
                            student_id,
                            slot
                        )
                    )

                assigned = True
                break

            if not assigned:
                raise ValueError(
                    f"Could not find a valid assignment "
                    f"for exam {exam.exam_id}"
                )

        return assignments