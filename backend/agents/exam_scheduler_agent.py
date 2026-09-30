from backend.services.schedule_planner import SchedulePlanner
from backend.validators.schedule_validator import ScheduleValidator
from backend.services.schedule_repair import ScheduleRepair
from backend.services.explanation_service import ExplanationService


class ExamSchedulerAgent:

    def __init__(self):
        self.planner = SchedulePlanner()
        self.validator = ScheduleValidator()
        self.repair_engine = ScheduleRepair()
        self.explanation_service = ExplanationService()
        self.current_schedule = []
        self.last_explanations = []

        print("🤖 Exam Scheduler Agent initialized")

    # ========================================================
    # NOTIFICATIONS
    # ========================================================

    def notify_assigned_faculty(self, exams, invigilators, assignments):
        exam_map = {exam.exam_id: exam for exam in exams}

        for assignment in assignments:
            exam = exam_map.get(assignment.exam_id)

            if not exam:
                continue

            for invigilator_id in assignment.invigilator_ids:
                invigilator = next(
                    (
                        faculty
                        for faculty in invigilators
                        if faculty.invigilator_id == invigilator_id
                    ),
                    None,
                )

                if not invigilator:
                    continue

                # Check whether this faculty member already had a notification for the same exam
                previous_notification = next(
                    (
                        notification
                        for notification in invigilator.notifications
                        if assignment.exam_id in notification
                        and "Assigned duty:" in notification
                    ),
                    None,
                )

                if previous_notification:
                    old_assignment = previous_notification.split("in ", 1)[-1]
                    new_assignment = f"{assignment.slot_id} / {assignment.room_id}"

                    if old_assignment != f"{new_assignment}. Please confirm your availability.":
                        message = (
                            f"🔔 Assignment Updated: {exam.subject} "
                            f"({exam.exam_id}) has been moved from "
                            f"{old_assignment.replace('. Please confirm your availability.', '')} "
                            f"to {new_assignment} due to schedule recovery. "
                            f"Please confirm your availability."
                        )

                        if message not in invigilator.notifications:
                            invigilator.notifications.append(message)
                            print(
                                f"🔔 Recovery notification sent to "
                                f"{invigilator.invigilator_id}: {message}"
                            )
                    continue

                message = (
                    f"🔔 Assigned duty: {exam.subject} "
                    f"({exam.exam_id}) "
                    f"in {assignment.slot_id} / "
                    f"{assignment.room_id}. "
                    f"Please confirm your availability."
                )

                if message not in invigilator.notifications:
                    invigilator.notifications.append(message)
                    print(
                        f"🔔 Notification sent to "
                        f"{invigilator.invigilator_id}: {message}"
                    )

    def notify_recovery_faculty(
        self,
        exams,
        invigilators,
        original_assignments,
        repaired_assignments,
        disruption_type="room",
        disrupted_invigilator_id="I02",
        disrupted_slot_id="T1",
    ):
        exam_map = {exam.exam_id: exam for exam in exams}
        original_map = {a.exam_id: a for a in original_assignments}
        repaired_map = {a.exam_id: a for a in repaired_assignments}

        for exam_id, orig in original_map.items():
            rep = repaired_map.get(exam_id)
            if not rep:
                continue
            exam = exam_map.get(exam_id)
            if not exam:
                continue

            room_changed = orig.room_id != rep.room_id
            invigilators_changed = orig.invigilator_ids != rep.invigilator_ids

            # Room change notifications
            if room_changed and not invigilators_changed:
                for invig_id in rep.invigilator_ids:
                    invig = next((f for f in invigilators if f.invigilator_id == invig_id), None)
                    if not invig:
                        continue
                    msg = (
                        f"🔔 Assignment Updated: {exam.subject} ({exam.exam_id}) "
                        f"has been moved from {orig.slot_id} / {orig.room_id} "
                        f"to {rep.slot_id} / {rep.room_id} due to schedule recovery. "
                        f"Please confirm your availability."
                    )
                    if msg not in invig.notifications:
                        invig.notifications.append(msg)
                        print(f"🔔 Recovery notification sent to {invig.invigilator_id}: {msg}")

            # Invigilator change notifications
            if invigilators_changed:
                # Newly assigned backup faculty
                for new_invig_id in rep.invigilator_ids:
                    if new_invig_id not in orig.invigilator_ids:
                        invig = next((f for f in invigilators if f.invigilator_id == new_invig_id), None)
                        if not invig:
                            continue
                        msg = (
                            f"🔔 Assignment Updated: {exam.subject} ({exam.exam_id}) "
                            f"reassigned from {disrupted_invigilator_id} to {new_invig_id} "
                            f"for {rep.slot_id} / {rep.room_id} because the original invigilator became unavailable. "
                            f"Please confirm your availability."
                        )
                        if msg not in invig.notifications:
                            invig.notifications.append(msg)
                            print(f"🔔 Recovery notification sent to {invig.invigilator_id}: {msg}")

                # Relieved faculty
                for old_invig_id in orig.invigilator_ids:
                    if old_invig_id not in rep.invigilator_ids:
                        invig = next((f for f in invigilators if f.invigilator_id == old_invig_id), None)
                        if not invig:
                            continue
                        msg = (
                            f"🔔 Duty Relieved: You have been relieved of duty for {exam.subject} "
                            f"({exam.exam_id}) in {orig.slot_id} / {orig.room_id} due to reported unavailability."
                        )
                        if msg not in invig.notifications:
                            invig.notifications.append(msg)
                            print(f"🔔 Relief notification sent to {invig.invigilator_id}: {msg}")

    # ========================================================
    # PLAN
    # ========================================================

    def plan_schedule(
        self,
        exams,
        rooms,
        invigilators,
    ):
        print("🧠 Agent → Schedule Planner")

        assignments = self.planner.plan(
            exams=exams,
            rooms=rooms,
            invigilators=invigilators,
        )

        self.current_schedule = assignments
        print("✅ Agent received planned schedule")

        return assignments

    # ========================================================
    # VALIDATE
    # ========================================================

    def validate_schedule(
        self,
        students,
        exams,
        rooms,
        invigilators,
        assignments,
    ):
        print("🔍 Agent → Schedule Validator")

        errors = self.validator.validate(
            students=students,
            exams=exams,
            rooms=rooms,
            invigilators=invigilators,
            assignments=assignments,
        )

        if not errors:
            print("✅ Validator: Schedule is VALID")
        else:
            print(f"⚠️ Validator: {len(errors)} violation(s) detected")
            for error in errors:
                print(f"   • {error}")

        return errors

    # ========================================================
    # REPAIR
    # ========================================================

    def repair_schedule(
        self,
        exams,
        rooms,
        invigilators,
        assignments,
    ):
        print("🔧 Agent → Schedule Repair Engine")

        repaired_assignments = self.repair_engine.repair(
            exams=exams,
            rooms=rooms,
            invigilators=invigilators,
            assignments=assignments,
        )

        print("✅ Agent received repaired schedule")

        return repaired_assignments

    # ========================================================
    # EXPLAIN
    # ========================================================

    def explain_repair(
        self,
        original_assignments,
        repaired_assignments,
        disruption_room="R102",
        disruption_slot="T1",
        disruption_type="room",
        disrupted_invigilator_id="I02",
    ):
        print("💬 Agent → Explanation Service")

        explanations = self.explanation_service.explain_repair(
            original_assignments=original_assignments,
            repaired_assignments=repaired_assignments,
            disruption_room=disruption_room,
            disruption_slot=disruption_slot,
            disruption_type=disruption_type,
            disrupted_invigilator_id=disrupted_invigilator_id,
        )

        print("✅ Agent received repair explanation")

        return explanations

    # ========================================================
    # AUTONOMOUS RECOVERY CYCLE
    # ========================================================

    def run_recovery_cycle(
        self,
        students,
        exams,
        rooms,
        invigilators,
        disruption_service,
        disruption_type="room",
        disrupted_room_id="R102",
        disrupted_invigilator_id="I02",
        disrupted_slot_id="T1",
    ):

        print("\n🤖 AGENT STARTING AUTONOMOUS RECOVERY CYCLE")
        print("=" * 55)

        # ====================================================
        # 1. PLAN
        # ====================================================

        print("\n🧠 STEP 1: PLANNING")

        assignments = self.plan_schedule(
            exams,
            rooms,
            invigilators,
        )

        # Notify the faculty members assigned by the planner.
        self.notify_assigned_faculty(
            exams=exams,
            invigilators=invigilators,
            assignments=assignments,
        )

        # ====================================================
        # 2. VALIDATE
        # ====================================================

        print("\n🔍 STEP 2: VALIDATING")

        errors = self.validate_schedule(
            students,
            exams,
            rooms,
            invigilators,
            assignments,
        )

        if errors:
            raise ValueError(
                "Initial schedule is invalid. "
                "Recovery cycle cannot continue."
            )

        # ====================================================
        # 3. DISRUPTION DETECTED
        # ====================================================

        print("\n⚠️ STEP 3: DISRUPTION DETECTED")

        if disruption_type == "room":
            (
                disrupted_assignments,
                disrupted_rooms,
            ) = disruption_service.room_unavailable(
                assignments,
                rooms,
                disrupted_room_id,
                disrupted_slot_id,
            )
            disrupted_invigilators = invigilators

            print(
                f"⚠️ Room {disrupted_room_id} "
                f"is unavailable in {disrupted_slot_id}"
            )

        elif disruption_type == "invigilator":
            (
                disrupted_assignments,
                disrupted_invigilators,
            ) = disruption_service.invigilator_unavailable(
                assignments,
                invigilators,
                disrupted_invigilator_id,
                disrupted_slot_id,
            )
            disrupted_rooms = rooms

            print(
                f"⚠️ Invigilator "
                f"{disrupted_invigilator_id} "
                f"is unavailable in {disrupted_slot_id}"
            )

        elif disruption_type in ("compound", "both"):
            (
                disrupted_assignments,
                disrupted_rooms,
            ) = disruption_service.room_unavailable(
                assignments,
                rooms,
                disrupted_room_id,
                disrupted_slot_id,
            )
            (
                disrupted_assignments,
                disrupted_invigilators,
            ) = disruption_service.invigilator_unavailable(
                disrupted_assignments,
                invigilators,
                disrupted_invigilator_id,
                disrupted_slot_id,
            )

            print(
                f"⚠️ Compound disruption: Room {disrupted_room_id} and "
                f"Invigilator {disrupted_invigilator_id} both unavailable in {disrupted_slot_id}"
            )

        else:
            raise ValueError(
                f"Unsupported disruption type: {disruption_type}"
            )

        # ====================================================
        # 4. DETECT VIOLATIONS
        # ====================================================

        print("\n🔎 STEP 4: DETECTING VIOLATIONS")

        disruption_errors = self.validate_schedule(
            students,
            exams,
            disrupted_rooms,
            disrupted_invigilators,
            disrupted_assignments,
        )

        if disruption_errors:
            print("🚨 Agent detected scheduling conflict(s) caused by the disruption.")
            for error in disruption_errors:
                print(f"   • {error}")
        else:
            print("ℹ️ No hard constraint violation detected after disruption.")

        # ====================================================
        # 5. REPAIR
        # ====================================================

        print("\n🔧 STEP 5: REPAIRING SCHEDULE")

        repaired_assignments = self.repair_schedule(
            exams,
            disrupted_rooms,
            disrupted_invigilators,
            disrupted_assignments,
        )

        # Update disruption state in live objects so portal reflects reality
        if disruption_type in ("invigilator", "compound", "both"):
            for inv in invigilators:
                if inv.invigilator_id == disrupted_invigilator_id and disrupted_slot_id in inv.available_slots:
                    inv.available_slots.remove(disrupted_slot_id)
        if disruption_type in ("room", "compound", "both"):
            for rm in rooms:
                if rm.room_id == disrupted_room_id and disrupted_slot_id in rm.available_slots:
                    rm.available_slots.remove(disrupted_slot_id)

        # Notify affected faculty members with specific recovery updates
        self.notify_recovery_faculty(
            exams=exams,
            invigilators=invigilators,
            original_assignments=disrupted_assignments,
            repaired_assignments=repaired_assignments,
            disruption_type=disruption_type,
            disrupted_invigilator_id=disrupted_invigilator_id,
            disrupted_slot_id=disrupted_slot_id,
        )

        # ====================================================
        # 5.5 EXPLAIN
        # ====================================================

        print("\n💬 STEP 5.5: EXPLAINING DECISION")

        explanations = self.explain_repair(
            original_assignments=disrupted_assignments,
            repaired_assignments=repaired_assignments,
            disruption_room=disrupted_room_id,
            disruption_slot=disrupted_slot_id,
            disruption_type=disruption_type,
            disrupted_invigilator_id=disrupted_invigilator_id,
        )

        for explanation in explanations:
            print("💡", explanation)

        self.last_explanations = explanations

        # ====================================================
        # 6. VERIFY
        # ====================================================

        print("\n🔍 STEP 6: VERIFYING REPAIR")

        final_errors = self.validate_schedule(
            students,
            exams,
            disrupted_rooms,
            disrupted_invigilators,
            repaired_assignments,
        )

        if final_errors:
            print("❌ Schedule verification FAILED")
            for error in final_errors:
                print(f"   • {error}")
            raise ValueError("Repaired schedule failed final validation.")

        print("✅ Schedule is VALID")
        print("✅ Repair verified successfully!")
        print("\n🤖 AGENT RECOVERY COMPLETE")
        print("=" * 55)

        self.current_schedule = repaired_assignments
        return repaired_assignments