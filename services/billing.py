import math
from datetime import datetime


def calculate_billing(hourly_rate, start_time, end_time):
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(end_time, str):
        end_time = datetime.fromisoformat(end_time)

    duration = end_time - start_time
    total_seconds = duration.total_seconds()
    total_hours = math.ceil(total_seconds / 3600)  # Round up to next hour
    if total_hours < 1:
        total_hours = 1
    total_amount = total_hours * hourly_rate
    return total_hours, round(total_amount, 2)


def calculate_prorated(hourly_rate, start_time, actual_end_time):
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    if isinstance(actual_end_time, str):
        actual_end_time = datetime.fromisoformat(actual_end_time)

    duration = actual_end_time - start_time
    total_seconds = duration.total_seconds()
    total_hours = math.ceil(total_seconds / 3600)
    if total_hours < 1:
        total_hours = 1
    total_amount = total_hours * hourly_rate
    return total_hours, round(total_amount, 2)
