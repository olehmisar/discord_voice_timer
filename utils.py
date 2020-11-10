from datetime import timedelta
from typing import Optional, Tuple


def parse_time_str(time_str: str) -> Optional[timedelta]:
    try:
        segments = list(map(int, time_str.strip().split(':')))
    except ValueError:
        return None

    if len(segments) == 1:
        minutes, seconds = segments[0], 0
    elif len(segments) == 2:
        minutes, seconds = segments
    else:
        return None

    return timedelta(minutes=minutes, seconds=seconds)


def to_minutes_seconds(td: timedelta) -> Tuple[int, int]:
    return td.seconds // 60, td.seconds % 60


def round_to_nearest_5(x: int) -> int:
    return int(5 * round(x / 5))


def calculate_notifications_interval(time_left: timedelta) -> timedelta:
    """Dynamically calculates how much time to wait between notification based on the time left"""

    minutes, seconds = to_minutes_seconds(time_left)
    if minutes > 5:
        return timedelta(minutes=1)

    elif minutes > 0:
        return timedelta(seconds=30)

    else:  # minutes == 0
        if seconds > 10:
            return timedelta(seconds=15)
        else:  # seconds <= 10
            return timedelta(seconds=5)
