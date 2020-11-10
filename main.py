import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import tempfile
from typing import Dict, Optional
from dataclasses import dataclass, field
from uuid import uuid4
import os


import discord
from discord.ext import commands

import pyttsx3

import dotenv
dotenv.load_dotenv()

from utils import calculate_notifications_interval, connect_to_voice_channel, get_user_voice_channel, parse_time_str, round_to_nearest_5
import texts


@dataclass
class TimerData:
    duration: timedelta
    voice_client: discord.VoiceClient
    start: datetime = field(default_factory=datetime.now)
    last_notified: datetime = field(default_factory=datetime.now)


@dataclass
class State:
    """Global state for a guild"""

    timer: Optional[TimerData] = None
    tts_engine: pyttsx3.Engine = field(default_factory=lambda: pyttsx3.init())

    def generate_voice(self, text: str):
        filename = os.path.join(
            tempfile.gettempdir(),
            f'discord_generated_voice_{uuid4()}.mp3'
        )

        self.tts_engine.save_to_file(text, filename)
        self.tts_engine.runAndWait()
        return discord.FFmpegPCMAudio(filename)

    def update_timer(self):
        timer = self.timer
        if not timer:
            return

        now = datetime.now()
        time_left = timer.duration - (now - timer.start)

        # Stop timer
        if time_left.seconds <= 0:
            self.timer = None

            timer.voice_client.stop()
            timer.voice_client.play(
                self.generate_voice(texts.en.time_is_over))

        # Notify if needed
        elif now - timer.last_notified > calculate_notifications_interval(time_left):
            timer.last_notified = now

            # Round to the nearest 5 seconds when the time is not that important yet
            if time_left.seconds > 30:
                time_left = timedelta(
                    seconds=round_to_nearest_5(time_left.seconds))

            timer.voice_client.stop()
            timer.voice_client.play(self.generate_voice(
                texts.en.timer_notification(time_left)))


# Global state for each guild
states: Dict[discord.Guild, State] = defaultdict(State)


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!')

    @bot.event
    async def on_ready(): print("Bot is ready!")

    @bot.command()
    async def start(ctx: commands.Context, duration_str=''):
        # Check if user is connected to a voice channel
        voice_channel = get_user_voice_channel(ctx)
        if not voice_channel:
            await ctx.send(f'{ctx.author.mention} {texts.en.requires_to_be_connected_to_a_voice_channel}')
            return

        # Parse duration string
        duration = parse_time_str(duration_str)
        if duration is None:
            await ctx.send(f'{ctx.author.mention} {texts.en.invalid_duration_str}: {duration_str}')
            return

        # Set a timer
        state = states[ctx.guild]

        def start_timer():
            state.timer = TimerData(
                duration=duration,
                voice_client=ctx.voice_client,
            )

        await connect_to_voice_channel(ctx, voice_channel)
        await ctx.message.add_reaction(texts.reactions.ok_hand)
        ctx.voice_client.stop()
        ctx.voice_client.play(state.generate_voice(texts.en.start_timer(duration)),
                              after=lambda _: start_timer())

    @bot.command()
    async def stop(ctx: commands.Context):
        await ctx.message.add_reaction(texts.reactions.ok_hand)
        state = states[ctx.guild]
        if ctx.voice_client:
            def stop_timer():
                state.timer = None
            ctx.voice_client.stop()
            ctx.voice_client.play(state.generate_voice(texts.en.timer_is_stopped),
                                  after=lambda _: stop_timer())

    async def update_timers():
        await bot.wait_until_ready()
        while not bot.is_closed():
            for state in states.values():
                state.update_timer()
            await asyncio.sleep(1)
    bot.loop.create_task(update_timers())

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
