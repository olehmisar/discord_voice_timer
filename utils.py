from datetime import timedelta
from typing import Optional, Tuple

import discord
from discord.ext.commands import Context


def get_user_voice_channel(ctx: Context) -> discord.VoiceChannel:
    return ctx.author.voice and ctx.author.voice.channel


async def connect_to_voice_channel(ctx: Context, voice_channel: discord.VoiceChannel):
    if not ctx.voice_client:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)


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

    if time_left > timedelta(minutes=5):
        return timedelta(minutes=1)

    elif time_left > timedelta(minutes=1):
        return timedelta(seconds=30)

    elif time_left > timedelta(seconds=15):
        return timedelta(seconds=15)

    else:  # seconds < 10
        return timedelta(seconds=5)
