"""Atomic single-process JSON booking storage (prototype only)."""
import json
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path

_lock = threading.RLock()


def _path():
    return Path(os.getenv("BOOKINGS_PATH", "data/bookings.json"))


def _read():
    path = _path()
    return json.loads(path.read_text()) if path.exists() else []


def _write(records):
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(records, indent=2))
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _validate(start_at, end_at):
    start, end = datetime.fromisoformat(start_at), datetime.fromisoformat(end_at)
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("Times must include timezone offsets")
    if start >= end:
        raise ValueError("End must be after start")
    return start, end


def _conflict(records, start, end, ignore=None):
    return any(
        r["id"] != ignore
        and start < datetime.fromisoformat(r["end_at"])
        and end > datetime.fromisoformat(r["start_at"])
        for r in records
    )


def list_bookings():
    """Return all appointments in the local demo dataset."""
    with _lock:
        return _read()


def create_booking(name: str, start_at: str, end_at: str):
    """Create an appointment. ISO 8601 times must have timezone offsets."""
    try:
        start, end = _validate(start_at, end_at)
        if not name.strip():
            raise ValueError("Name is required")
        with _lock:
            records = _read()
            if _conflict(records, start, end):
                return {"error": "Time slot overlaps an existing appointment"}
            booking = {"id": str(uuid.uuid4()), "name": name.strip(),
                       "start_at": start_at, "end_at": end_at}
            records.append(booking)
            _write(records)
            return booking
    except (ValueError, TypeError) as exc:
        return {"error": str(exc)}


def update_booking(booking_id: str, name: str, start_at: str, end_at: str):
    """Update appointment by ID after checking for time conflicts."""
    try:
        start, end = _validate(start_at, end_at)
        if not name.strip():
            raise ValueError("Name is required")
        with _lock:
            records = _read()
            target = next((r for r in records if r["id"] == booking_id), None)
            if target is None:
                return {"error": "Booking not found"}
            if _conflict(records, start, end, booking_id):
                return {"error": "Time slot overlaps an existing appointment"}
            target.update(name=name.strip(), start_at=start_at, end_at=end_at)
            _write(records)
            return target
    except (ValueError, TypeError) as exc:
        return {"error": str(exc)}


def delete_booking(booking_id: str):
    """Delete a booking by ID; only call after user confirmation."""
    with _lock:
        records = _read()
        updated = [r for r in records if r["id"] != booking_id]
        if len(updated) == len(records):
            return {"error": "Booking not found"}
        _write(updated)
        return {"deleted": booking_id}
