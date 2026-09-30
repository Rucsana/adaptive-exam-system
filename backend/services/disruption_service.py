from backend.models.assignment import Assignment
from backend.models.room import Room
from backend.models.invigilator import Invigilator


class DisruptionService:

    # ========================================================
    # ROOM UNAVAILABLE
    # ========================================================

    def room_unavailable(
        self,
        assignments: list[Assignment],
        rooms: list[Room],
        room_id: str,
        slot_id: str,
    ) -> tuple[list[Assignment], list[Room]]:

        disrupted_assignments = list(assignments)
        disrupted_rooms = []

        for room in rooms:

            if room.room_id == room_id:

                new_available_slots = [
                    slot
                    for slot in room.available_slots
                    if slot != slot_id
                ]

                disrupted_rooms.append(
                    Room(
                        room_id=room.room_id,
                        building=room.building,
                        floor=room.floor,
                        capacity=room.capacity,
                        available_slots=new_available_slots,
                        accessibility_features=room.accessibility_features,
                    )
                )

            else:
                disrupted_rooms.append(room)

        return disrupted_assignments, disrupted_rooms

    # ========================================================
    # INVIGILATOR UNAVAILABLE
    # ========================================================

    def invigilator_unavailable(
        self,
        assignments: list[Assignment],
        invigilators: list[Invigilator],
        invigilator_id: str,
        slot_id: str,
    ) -> tuple[list[Assignment], list[Invigilator]]:

        disrupted_assignments = list(assignments)
        disrupted_invigilators = []

        for invigilator in invigilators:

            if invigilator.invigilator_id == invigilator_id:

                new_available_slots = [
                    slot
                    for slot in invigilator.available_slots
                    if slot != slot_id
                ]

                disrupted_invigilators.append(
                    Invigilator(
                        invigilator_id=invigilator.invigilator_id,
                        name=invigilator.name,
                        department=invigilator.department,
                        available_slots=new_available_slots,
                        confirmed_slots=invigilator.confirmed_slots.copy(),
                        checked_in_slots=invigilator.checked_in_slots.copy(),
                        assigned_slots=invigilator.assigned_slots.copy(),
                        notifications=invigilator.notifications,
                        block=invigilator.block,
                        password=invigilator.password,
                    )
                )

            else:
                disrupted_invigilators.append(invigilator)

        return disrupted_assignments, disrupted_invigilators