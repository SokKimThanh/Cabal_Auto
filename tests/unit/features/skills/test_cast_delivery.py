import time

from lib.features.skills.cast_delivery import CastDeliveryManager, CastReservation


def test_cast_delivery_manager_add_remove():
    manager = CastDeliveryManager()
    reservation = CastReservation(token="t1", key="1", skill_name="Fireball", lane="attack", created_at=time.time(), expected_strategy="combo")
    manager.add_reservation(reservation)

    assert manager.get_reservation("t1") == reservation
    assert manager.has_reservation_for_lane("attack") is True

    manager.remove_reservation("t1")
    assert manager.get_reservation("t1") is None
    assert manager.has_reservation_for_lane("attack") is False

def test_cast_delivery_manager_lane_limit():
    manager = CastDeliveryManager()
    r1 = CastReservation(token="t1", key="1", skill_name="Fireball", lane="attack", created_at=time.time(), expected_strategy="combo")
    manager.add_reservation(r1)

    r2 = CastReservation(token="t2", key="2", skill_name="Iceball", lane="attack", created_at=time.time(), expected_strategy="combo")
    manager.add_reservation(r2)

    # Adding a new reservation to the same lane should replace the old one
    assert manager.get_reservation("t1") is None
    assert manager.get_reservation("t2") == r2
