import asyncio
from datetime import datetime, timedelta
import tempfile
from typing import Dict
from dataclasses import dataclass
from uuid import uuid4
import os


import discord
from discord.ext import commands

import pyttsx3

import dotenv
dotenv.load_dotenv()

from utils import calculate_notifications_interval, parse_time_str, round_to_nearest_5
import texts


@dataclass
class TimerData:
    start: datetime
    notifications_interval: timedelta
    duration: timedelta
    voice_client: discord.VoiceClient
    last_notified: datetime


class state:
    """Just a namespace for the global state"""

    timers: Dict[int, TimerData] = {}
    tts_engine = pyttsx3.init()


def generate_voice(text: str):
    filename = os.path.join(
        tempfile.gettempdir(),
        f'discord_generated_voice_{uuid4()}.mp3'
    )

    state.tts_engine.save_to_file(text, filename)
    state.tts_engine.runAndWait()
    return discord.FFmpegPCMAudio(filename)


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!')

    @bot.event
    async def on_ready(): print("Bot is ready!")

    @bot.command()
    async def start(ctx: commands.Context, duration_str=''):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(f'{ctx.author.mention} {texts.en.requires_to_be_connected_to_a_voice_channel}')
            return

        # Parse duration string
        duration = parse_time_str(duration_str)
        if duration is None:
            await ctx.send(f'{ctx.author.mention} {texts.en.invalid_duration_str}: {duration_str}')
            return

        # Connect to this user's voice channel
        voice_channel: discord.VoiceChannel = ctx.author.voice.channel
        if not ctx.voice_client or ctx.voice_client.channel != voice_channel:
            await voice_channel.connect()

        # Set a timer
        def start_timer():
            state.timers[voice_channel.id] = TimerData(
                start=datetime.now(),
                duration=duration,
                notifications_interval=timedelta(seconds=5),
                last_notified=datetime.now(),
                voice_client=ctx.voice_client,
            )

        ctx.voice_client.stop()
        ctx.voice_client.play(generate_voice(texts.en.start_timer(duration)),
                              after=lambda _: start_timer())

    async def update_timers():
        await bot.wait_until_ready()
        while not bot.is_closed():
            # cache keys because the dictionary will be modified during iteration
            for id in list(state.timers.keys()):
                timer = state.timers[id]
                now = datetime.now()

                time_left = timer.duration - (now - timer.start)

                # Stop timer
                if time_left.seconds <= 0:
                    del state.timers[id]

                    timer.voice_client.stop()
                    timer.voice_client.play(
                        generate_voice(texts.en.time_is_over))

                # Notify if needed
                elif now - timer.last_notified > calculate_notifications_interval(time_left):
                    timer.last_notified = now

                    # Round to the nearest 5 seconds when the time is not that important yet
                    if time_left.seconds > 30:
                        time_left = timedelta(
                            seconds=round_to_nearest_5(time_left.seconds))

                    timer.voice_client.stop()
                    timer.voice_client.play(generate_voice(
                        texts.en.timer_notification(time_left)))

            await asyncio.sleep(1)

    bot.loop.create_task(update_timers())

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
