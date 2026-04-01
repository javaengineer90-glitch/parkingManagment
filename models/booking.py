from db import get_db


def create_booking(spot_id, booked_by, vehicle_number, vehicle_type, start_time, end_time, total_hours, total_amount):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO bookings (spot_id, booked_by, vehicle_number, vehicle_type, start_time, end_time, total_hours, total_amount)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (spot_id, booked_by, vehicle_number, vehicle_type, start_time, end_time, total_hours, total_amount)
    )
    db.commit()
    return cursor.lastrowid


def get_booking_by_id(booking_id):
    db = get_db()
    return db.execute(
        """SELECT b.*, ps.spot_number, ps.hourly_rate, ps.owner_id,
                  u.name as booker_name, u.flat_number as booker_flat,
                  o.name as owner_name
           FROM bookings b
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users u ON b.booked_by = u.id
           JOIN users o ON ps.owner_id = o.id
           WHERE b.id = ?""",
        (booking_id,)
    ).fetchone()


def get_bookings_by_user(user_id):
    db = get_db()
    return db.execute(
        """SELECT b.*, ps.spot_number, ps.hourly_rate, o.name as owner_name
           FROM bookings b
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users o ON ps.owner_id = o.id
           WHERE b.booked_by = ?
           ORDER BY b.created_at DESC""",
        (user_id,)
    ).fetchall()


def get_active_bookings_by_user(user_id):
    db = get_db()
    return db.execute(
        """SELECT b.*, ps.spot_number, ps.hourly_rate, o.name as owner_name
           FROM bookings b
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users o ON ps.owner_id = o.id
           WHERE b.booked_by = ? AND b.status = 'active'
           ORDER BY b.start_time ASC""",
        (user_id,)
    ).fetchall()


def get_bookings_for_spot_owner(owner_id):
    db = get_db()
    return db.execute(
        """SELECT b.*, ps.spot_number, u.name as booker_name, u.flat_number as booker_flat
           FROM bookings b
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users u ON b.booked_by = u.id
           WHERE ps.owner_id = ?
           ORDER BY b.created_at DESC""",
        (owner_id,)
    ).fetchall()


def end_booking(booking_id, actual_end_time, total_hours, total_amount):
    db = get_db()
    db.execute(
        """UPDATE bookings SET actual_end_time = ?, total_hours = ?, total_amount = ?, status = 'completed'
           WHERE id = ?""",
        (actual_end_time, total_hours, total_amount, booking_id)
    )
    db.commit()


def cancel_booking(booking_id):
    db = get_db()
    db.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    db.commit()


def check_spot_conflict(spot_id, start_time, end_time):
    db = get_db()
    return db.execute(
        """SELECT id FROM bookings
           WHERE spot_id = ? AND status = 'active'
           AND start_time < ? AND end_time > ?""",
        (spot_id, end_time, start_time)
    ).fetchone()


def get_all_bookings():
    db = get_db()
    return db.execute(
        """SELECT b.*, ps.spot_number, u.name as booker_name, u.flat_number as booker_flat,
                  o.name as owner_name
           FROM bookings b
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users u ON b.booked_by = u.id
           JOIN users o ON ps.owner_id = o.id
           ORDER BY b.created_at DESC"""
    ).fetchall()


def get_active_bookings_for_spots(spot_ids):
    if not spot_ids:
        return []
    db = get_db()
    placeholders = ','.join('?' * len(spot_ids))
    return db.execute(
        f"""SELECT b.spot_id, b.start_time, b.end_time, b.vehicle_number, b.vehicle_type,
                   u.name as guest_name, u.flat_number as guest_flat, u.phone as guest_phone
           FROM bookings b
           JOIN users u ON b.booked_by = u.id
           WHERE b.spot_id IN ({placeholders}) AND b.status = 'active'
           ORDER BY b.start_time ASC""",
        spot_ids
    ).fetchall()


def get_active_bookings_count():
    db = get_db()
    row = db.execute("SELECT COUNT(*) as cnt FROM bookings WHERE status = 'active'").fetchone()
    return row['cnt']
