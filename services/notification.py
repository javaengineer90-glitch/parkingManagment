from models.notification import create_notification


def notify_booking_confirmed(booker_id, spot_number, start_time, end_time):
    message = f"Your booking for spot {spot_number} is confirmed from {start_time} to {end_time}."
    create_notification(booker_id, 'booking_confirmed', message)


def notify_spot_booked(owner_id, spot_number, booker_name, start_time, end_time):
    message = f"Your spot {spot_number} has been booked by {booker_name} from {start_time} to {end_time}."
    create_notification(owner_id, 'spot_booked', message)


def notify_payment_received(owner_id, amount, spot_number, payer_name):
    message = f"Payment of Rs. {amount} received from {payer_name} for spot {spot_number}."
    create_notification(owner_id, 'payment_received', message)


def notify_booking_ended(booker_id, spot_number, total_amount):
    message = f"Your booking for spot {spot_number} has ended. Total charge: Rs. {total_amount}."
    create_notification(booker_id, 'booking_ended', message)


def notify_booking_cancelled(owner_id, spot_number, booker_name):
    message = f"Booking for spot {spot_number} by {booker_name} has been cancelled."
    create_notification(owner_id, 'booking_cancelled', message)
