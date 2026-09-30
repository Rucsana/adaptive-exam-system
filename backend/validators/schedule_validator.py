from backend.models.student import Student
from backend.models.exam import Exam
from backend.models.room import Room
from backend.models.invigilator import Invigilator
from backend.models.assignment import Assignment


class ScheduleValidator:

    def validate(
        self,
        students: list[Student],
        exams: list[Exam],
        rooms: list[Room],
        invigilators: list[Invigilator],
        assignments: list[Assignment],
    ) -> list[str]:

        errors = []

        exam_map = {
            exam.exam_id: exam
            for exam in exams
        }

        room_map = {
            room.room_id: room
            for room in rooms
        }

        invigilator_map = {
            inv.invigilator_id: inv
            for inv in invigilators
        }

        student_map = {
            student.student_id: student
            for student in students
        }

        # =========================================================
        # H1: No student can have overlapping exams
        # =========================================================

        student_exam_slots = {}

        for assignment in assignments:

            exam = exam_map.get(assignment.exam_id)

            if not exam:
                errors.append(
                    f"Unknown exam: {assignment.exam_id}"
                )
                continue

            for student_id in exam.students:

                key = (student_id, assignment.slot_id)

                if key in student_exam_slots:
                    errors.append(
                        f"Student {student_id} has overlapping exams "
                        f"in slot {assignment.slot_id}"
                    )

                student_exam_slots[key] = assignment.exam_id

        # =========================================================
        # H2: Room capacity
        # =========================================================

        for assignment in assignments:

            exam = exam_map.get(assignment.exam_id)
            room = room_map.get(assignment.room_id)

            if not exam or not room:
                continue

            if room.capacity < len(exam.students):

                errors.append(
                    f"Room {room.room_id} capacity ({room.capacity}) "
                    f"is insufficient for exam {exam.exam_id} "
                    f"({len(exam.students)} students)"
                )

        # =========================================================
        # H3: Room availability
        # =========================================================

        for assignment in assignments:

            room = room_map.get(assignment.room_id)

            if room and assignment.slot_id not in room.available_slots:

                errors.append(
                    f"Room {room.room_id} is unavailable "
                    f"in slot {assignment.slot_id}"
                )

        # =========================================================
        # H3b: Room double-booking
        # =========================================================

        room_slots = set()

        for assignment in assignments:

            key = (
                assignment.room_id,
                assignment.slot_id
            )

            if key in room_slots:

                errors.append(
                    f"Room {assignment.room_id} is double-booked "
                    f"in slot {assignment.slot_id}"
                )

            room_slots.add(key)

        # =========================================================
        # H4 + H5 + H6:
        # Invigilator availability, confirmation,
        # check-in and double booking
        # =========================================================

        invigilator_slots = set()

        for assignment in assignments:

            for invigilator_id in assignment.invigilator_ids:

                invigilator = invigilator_map.get(
                    invigilator_id
                )

                if not invigilator:

                    errors.append(
                        f"Unknown invigilator: "
                        f"{invigilator_id}"
                    )

                    continue

                # H4: Timetable availability
                if (
                    assignment.slot_id
                    not in invigilator.available_slots
                ):

                    errors.append(
                        f"Invigilator {invigilator_id} "
                        f"is unavailable in slot "
                        f"{assignment.slot_id}"
                    )

                # H5: Faculty confirmation
                if (
                    assignment.slot_id
                    not in invigilator.confirmed_slots
                ):

                    errors.append(
                        f"Invigilator {invigilator_id} "
                        f"has not confirmed availability "
                        f"for slot {assignment.slot_id}"
                    )

                # H6: Physical/current availability
                if (
                    assignment.slot_id
                    not in invigilator.checked_in_slots
                ):

                    errors.append(
                        f"Invigilator {invigilator_id} "
                        f"is not checked in for slot "
                        f"{assignment.slot_id}"
                    )

                # H7: Invigilator double booking
                key = (
                    invigilator_id,
                    assignment.slot_id
                )

                if key in invigilator_slots:

                    errors.append(
                        f"Invigilator {invigilator_id} "
                        f"is double-booked in slot "
                        f"{assignment.slot_id}"
                    )

                invigilator_slots.add(key)

        # =========================================================
        # H8: Accessibility requirements
        # =========================================================

        for assignment in assignments:

            room = room_map.get(assignment.room_id)
            exam = exam_map.get(assignment.exam_id)

            if not room or not exam:
                continue

            for student_id in exam.students:

                student = student_map.get(student_id)

                if not student:
                    continue

                requirement = (
                    student.accessibility_requirement
                )

                if (
                    requirement
                    and requirement
                    not in room.accessibility_features
                ):

                    errors.append(
                        f"Room {room.room_id} does not satisfy "
                        f"accessibility requirement "
                        f"'{requirement}' "
                        f"for student {student_id}"
                    )

        return errors