from db import get_db


def create_payment(booking_id, payer_id, amount, payment_method='online', transaction_id=None, status='pending'):
    db = get_db()
    cursor = db.execute(
        """INSERT INTO payments (booking_id, payer_id, amount, payment_method, transaction_id, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (booking_id, payer_id, amount, payment_method, transaction_id, status)
    )
    db.commit()
    return cursor.lastrowid


def get_payment_by_id(payment_id):
    db = get_db()
    return db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()


def get_payment_by_booking(booking_id):
    db = get_db()
    return db.execute("SELECT * FROM payments WHERE booking_id = ?", (booking_id,)).fetchone()


def update_payment_status(payment_id, status, transaction_id=None):
    db = get_db()
    if transaction_id:
        db.execute("UPDATE payments SET status = ?, transaction_id = ? WHERE id = ?",
                   (status, transaction_id, payment_id))
    else:
        db.execute("UPDATE payments SET status = ? WHERE id = ?", (status, payment_id))
    db.commit()


def get_payments_by_user(user_id):
    db = get_db()
    return db.execute(
        """SELECT p.*, b.spot_id, b.vehicle_number, ps.spot_number
           FROM payments p
           JOIN bookings b ON p.booking_id = b.id
           JOIN parking_spots ps ON b.spot_id = ps.id
           WHERE p.payer_id = ?
           ORDER BY p.created_at DESC""",
        (user_id,)
    ).fetchall()


def get_earnings_by_owner(owner_id):
    db = get_db()
    return db.execute(
        """SELECT p.*, b.vehicle_number, ps.spot_number, u.name as payer_name
           FROM payments p
           JOIN bookings b ON p.booking_id = b.id
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users u ON p.payer_id = u.id
           WHERE ps.owner_id = ? AND p.status = 'completed'
           ORDER BY p.created_at DESC""",
        (owner_id,)
    ).fetchall()


def get_total_revenue():
    db = get_db()
    row = db.execute("SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = 'completed'").fetchone()
    return row['total']


def get_revenue_today():
    db = get_db()
    row = db.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM payments WHERE status = 'completed' AND date(created_at) = date('now')"
    ).fetchone()
    return row['total']


def get_revenue_this_month():
    db = get_db()
    row = db.execute(
        """SELECT COALESCE(SUM(amount), 0) as total FROM payments
           WHERE status = 'completed' AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"""
    ).fetchone()
    return row['total']


def get_all_payments():
    db = get_db()
    return db.execute(
        """SELECT p.*, b.vehicle_number, ps.spot_number, u.name as payer_name, o.name as owner_name
           FROM payments p
           JOIN bookings b ON p.booking_id = b.id
           JOIN parking_spots ps ON b.spot_id = ps.id
           JOIN users u ON p.payer_id = u.id
           JOIN users o ON ps.owner_id = o.id
           ORDER BY p.created_at DESC"""
    ).fetchall()


def get_daily_revenue(days=30):
    db = get_db()
    return db.execute(
        """SELECT date(created_at) as day, SUM(amount) as total
           FROM payments WHERE status = 'completed'
           AND created_at >= date('now', ?)
           GROUP BY date(created_at) ORDER BY day""",
        (f'-{days} days',)
    ).fetchall()
