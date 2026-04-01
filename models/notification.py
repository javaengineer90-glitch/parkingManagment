from db import get_db


def create_notification(user_id, notif_type, message):
    db = get_db()
    db.execute(
        "INSERT INTO notifications (user_id, type, message) VALUES (?, ?, ?)",
        (user_id, notif_type, message)
    )
    db.commit()


def get_notifications(user_id, limit=20):
    db = get_db()
    return db.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()


def get_unread_count(user_id):
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    return row['cnt']


def mark_as_read(notification_id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    db.commit()


def mark_all_read(user_id):
    db = get_db()
    db.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    db.commit()
