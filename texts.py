from datetime import timedelta
from utils import to_minutes_seconds


class en:
    _language_name = 'english'

    requires_to_be_connected_to_a_voice_channel = 'you must be connected to a voice channel to use this command'
    invalid_duration_str = 'invalid duration'

    time_is_over = 'time is over'
    timer_is_stopped = 'timer is stopped'

    @staticmethod
    def start_timer(duration: timedelta):
        return f'setting a timer for {en._to_time_str(duration, include_flat=True)}. 3, 2, 1, GO!'

    @staticmethod
    def timer_notification(time_left: timedelta) -> str:
        return f'{en._to_time_str(time_left)} left'

    invalid_index = 'invalid index'
    voice_set_successfully = 'voice was set successfully'
    language_changed_to = 'language was changed to'

    @staticmethod
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


class ru:
    _language_name = 'russian'

    requires_to_be_connected_to_a_voice_channel = 'вы должны быть присоединены к голосовому чату, чтобы использовать эту команду'
    invalid_duration_str = 'неверное время'

    time_is_over = 'время вышло'
    timer_is_stopped = 'таймер остановлен'

    @staticmethod
    def start_timer(duration: timedelta):
        return f'запускаю таймер на {ru._to_time_str(duration)}. 3, 2, 1, Время пошло!'

    @staticmethod
    def timer_notification(time_left: timedelta) -> str:
        return f'осталось {ru._to_time_str(time_left)}'

    @staticmethod
    def _to_time_str(time: timedelta) -> str:
        minutes, seconds = to_minutes_seconds(time)
        ret = ''
        if minutes != 0:
            ret += f'{minutes} {"минута" if minutes == 1 else "минут"}'

        if minutes == 0 or seconds != 0:
            ret += f'{seconds} {"секунда" if seconds == 1 else "секунд"}'

        return ret

    invalid_index = 'неверный индекс'
    voice_set_successfully = 'голос успешно изменен'
    language_changed_to = 'язык изменен на'


texts = {'en': en, 'ru': ru}


class reactions:
    ok_hand = '👌'
