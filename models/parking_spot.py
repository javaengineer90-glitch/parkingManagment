from db import get_db


def create_spot(owner_id, spot_number, location_description, hourly_rate, available_from, available_until):
    db = get_db()
    db.execute(
        """INSERT INTO parking_spots (owner_id, spot_number, location_description, hourly_rate, available_from, available_until)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (owner_id, spot_number, location_description, hourly_rate, available_from, available_until)
    )
    db.commit()


def get_spot_by_id(spot_id):
    db = get_db()
    return db.execute("SELECT * FROM parking_spots WHERE id = ?", (spot_id,)).fetchone()


def get_available_spots():
    db = get_db()
    return db.execute(
        """SELECT ps.*, u.name as owner_name, u.flat_number
           FROM parking_spots ps JOIN users u ON ps.owner_id = u.id
           WHERE ps.is_available = 1
           ORDER BY ps.hourly_rate ASC"""
    ).fetchall()


def get_spots_by_owner(owner_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM parking_spots WHERE owner_id = ? ORDER BY created_at DESC",
        (owner_id,)
    ).fetchall()


def update_spot(spot_id, spot_number, location_description, hourly_rate, available_from, available_until):
    db = get_db()
    db.execute(
        """UPDATE parking_spots SET spot_number = ?, location_description = ?, hourly_rate = ?,
           available_from = ?, available_until = ? WHERE id = ?""",
        (spot_number, location_description, hourly_rate, available_from, available_until, spot_id)
    )
    db.commit()


def toggle_spot_availability(spot_id):
    db = get_db()
    db.execute(
        "UPDATE parking_spots SET is_available = CASE WHEN is_available = 1 THEN 0 ELSE 1 END WHERE id = ?",
        (spot_id,)
    )
    db.commit()


def get_all_spots():
    db = get_db()
    return db.execute(
        """SELECT ps.*, u.name as owner_name, u.flat_number
           FROM parking_spots ps JOIN users u ON ps.owner_id = u.id
           ORDER BY ps.created_at DESC"""
    ).fetchall()


def delete_spot(spot_id):
    db = get_db()
    db.execute("DELETE FROM parking_spots WHERE id = ?", (spot_id,))
    db.commit()
