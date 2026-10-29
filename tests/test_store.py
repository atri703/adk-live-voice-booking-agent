from app import store


def test_create_update_delete_and_conflicts(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_PATH", str(tmp_path / "bookings.json"))
    a = store.create_booking("Alex", "2026-11-01T10:00:00+05:30", "2026-11-01T11:00:00+05:30")
    assert "id" in a
    assert len(store.list_bookings()) == 1
    assert "error" in store.create_booking("Bob", "2026-11-01T10:30:00+05:30", "2026-11-01T11:30:00+05:30")
    assert "error" in store.create_booking("Bob", "2026-11-01T11:00:00", "2026-11-01T12:00:00")
    updated = store.update_booking(a["id"], "Alex", "2026-11-01T12:00:00+05:30", "2026-11-01T13:00:00+05:30")
    assert updated["start_at"].endswith("12:00:00+05:30")
    assert store.delete_booking(a["id"]) == {"deleted": a["id"]}
    assert store.list_bookings() == []
    assert "error" in store.delete_booking(a["id"])


def test_invalid_times(tmp_path, monkeypatch):
    monkeypatch.setenv("BOOKINGS_PATH", str(tmp_path / "bookings.json"))
    assert "error" in store.create_booking("Alex", "bad", "bad")
    assert "error" in store.create_booking("Alex", "2026-11-01T12:00:00+00:00", "2026-11-01T11:00:00+00:00")
