from datetime import timedelta
from utils import to_minutes_seconds


class en:
    requires_to_be_connected_to_a_voice_channel = 'you must be connected to a voice channel to use this command'
    invalid_duration_str = 'invalid duration'

    time_is_over = 'time is over'
    timer_is_stopped = 'timer is stopped'

    @staticmethod
    def start_timer(duration: timedelta):
        return f'setting a timer for {_to_time_str(duration, include_flat=True)}. 3, 2, 1, GO!'

    @staticmethod
    def timer_notification(time_left: timedelta) -> str:
        return f'{_to_time_str(time_left)} left'


def _to_time_str(time: timedelta, include_flat=False) -> str:
    minutes, seconds = to_minutes_seconds(time)
    ret = ''
    if minutes != 0:
        ret += f'{minutes} {"minute" if minutes == 1 else "minutes"}'

    if minutes == 0 or seconds != 0:
        ret += f'{seconds} {"second" if seconds == 1 else "seconds"}'
    elif include_flat:
        ret += 'flat'

    return ret
