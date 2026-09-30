from backend.services.llm_service import LLMService


class ExplanationService:

    def __init__(self):
        self.llm = LLMService()

    def explain_repair(
        self,
        original_assignments,
        repaired_assignments,
        disruption_room="R102",
        disruption_slot="T1",
        disruption_type="room",
        disrupted_invigilator_id=None,
    ):
        explanations = []

        # Backward compatibility: if caller passed an invigilator ID into disruption_room
        if str(disruption_room).startswith("I") and not disrupted_invigilator_id:
            disrupted_invigilator_id = disruption_room
            disruption_type = "invigilator"

        original_map = {
            assignment.exam_id: assignment
            for assignment in original_assignments
        }

        repaired_map = {
            assignment.exam_id: assignment
            for assignment in repaired_assignments
        }

        for exam_id, original in original_map.items():
            repaired = repaired_map.get(exam_id)

            if repaired is None:
                continue

            room_changed = original.room_id != repaired.room_id
            slot_changed = original.slot_id != repaired.slot_id
            invigilators_changed = original.invigilator_ids != repaired.invigilator_ids

            if room_changed or slot_changed or invigilators_changed:
                old_invigs = ", ".join(original.invigilator_ids)
                new_invigs = ", ".join(repaired.invigilator_ids)

                if disruption_type in ("compound", "both") or (room_changed and invigilators_changed):
                    invig_target = disrupted_invigilator_id or old_invigs
                    explanation = (
                        f"Exam {exam_id} was affected by compound disruption in slot {disruption_slot} "
                        f"(room {disruption_room} and invigilator {invig_target} both became unavailable). "
                        f"The agent relocated the exam to room {repaired.room_id} and reassigned duty "
                        f"to backup faculty {new_invigs}. The remaining exams were preserved where possible."
                    )
                    ai_rationale = self.llm.generate_repair_explanation(
                        disruption_type="compound",
                        disrupted_id=f"{disruption_room} & {invig_target}",
                        slot_id=disruption_slot,
                        affected_exam=exam_id,
                        original_location=f"{original.slot_id} / {original.room_id} ({old_invigs})",
                        repaired_location=f"{repaired.slot_id} / {repaired.room_id}",
                        backup_invigilator=new_invigs,
                    )
                elif disruption_type == "invigilator" or invigilators_changed:
                    invig_target = disrupted_invigilator_id or old_invigs
                    explanation = (
                        f"Exam {exam_id} was affected because invigilator {invig_target} "
                        f"became unavailable in slot {disruption_slot}. "
                        f"The agent selected valid backup faculty {new_invigs} for "
                        f"{repaired.slot_id} / {repaired.room_id}. "
                        f"The remaining exams were preserved where possible."
                    )
                    ai_rationale = self.llm.generate_repair_explanation(
                        disruption_type="invigilator",
                        disrupted_id=invig_target,
                        slot_id=disruption_slot,
                        affected_exam=exam_id,
                        original_location=f"{original.slot_id} / {original.room_id} ({old_invigs})",
                        repaired_location=f"{repaired.slot_id} / {repaired.room_id}",
                        backup_invigilator=new_invigs,
                    )
                else:
                    explanation = (
                        f"Exam {exam_id} was affected because "
                        f"room {disruption_room} became unavailable "
                        f"in slot {disruption_slot}. "
                        f"The agent changed the assignment from "
                        f"{original.slot_id} / {original.room_id} "
                        f"to "
                        f"{repaired.slot_id} / {repaired.room_id}. "
                        f"The remaining exams were preserved "
                        f"where possible."
                    )
                    ai_rationale = self.llm.generate_repair_explanation(
                        disruption_type="room",
                        disrupted_id=disruption_room,
                        slot_id=disruption_slot,
                        affected_exam=exam_id,
                        original_location=f"{original.slot_id} / {original.room_id}",
                        repaired_location=f"{repaired.slot_id} / {repaired.room_id}",
                    )

                explanations.append(explanation)
                if ai_rationale:
                    explanations.append(ai_rationale)

        if not explanations:
            explanations.append(
                "No exam assignments required changes."
            )

        return explanations