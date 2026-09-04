from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class TransportStatus(Enum):
    SENT = "sent"
    FAILED = "failed"

class CastOutcome(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNVERIFIED = "unverified"
    CANCELLED = "cancelled"

@dataclass
class CastReservation:
    token: str
    key: str
    skill_name: str
    lane: str
    created_at: float
    expected_strategy: str

class CastDeliveryManager:
    def __init__(self):
        self.pending_reservations: Dict[str, CastReservation] = {}

    def add_reservation(self, reservation: CastReservation):
        # Allow one reservation per lane
        existing_tokens = [k for k, v in self.pending_reservations.items() if v.lane == reservation.lane]
        for token in existing_tokens:
            del self.pending_reservations[token]
        self.pending_reservations[reservation.token] = reservation

    def get_reservation(self, token: str) -> Optional[CastReservation]:
        return self.pending_reservations.get(token)

    def remove_reservation(self, token: str) -> Optional[CastReservation]:
        if token in self.pending_reservations:
            return self.pending_reservations.pop(token)
        return None

    def has_reservation_for_lane(self, lane: str) -> bool:
        for r in self.pending_reservations.values():
            if r.lane == lane:
                return True
        return False
