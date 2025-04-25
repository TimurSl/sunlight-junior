import asyncio
import random
from dataclasses import dataclass
from typing import List

import discord
from discord.ext import commands
import yt_dlp

@dataclass
class TrackInfo:
    url: str
    title: str
    stream_url: str



class GuildMusic:
    def __init__(self):
        self.queue: List[TrackInfo] = []
        self.current_index = 0
        self.loop247 = False
        self.random_mode = False
        self.loop_queue = False
        self.vc = None

class MusicController:
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'noplaylist': False,
        'quiet': True,
        'extract_flat': 'in_playlist'
    }
    FFMPEG_OPTIONS = {
        'options': '-vn'
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ytdl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)
        self.guilds = {}
        self.skip_flag = False

    def get_guild_music(self, guild_id: int) -> GuildMusic:
        if guild_id not in self.guilds:
            self.guilds[guild_id] = GuildMusic()
        return self.guilds[guild_id]

    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You're not in a voice channel.")
            return
        channel = interaction.user.voice.channel
        guild_music = self.get_guild_music(interaction.guild.id)
        guild_music.vc = await channel.connect()
        await interaction.followup.send(f"Joined {channel.name}")

    async def leave(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if guild_music.vc and guild_music.vc.is_connected():
            await guild_music.vc.disconnect()
            guild_music.vc = None
            guild_music.queue.clear()
            guild_music.current_index = 0
            await interaction.followup.send("Left the voice channel.")

    async def play(self, interaction: discord.Interaction, url: str):
        guild_music = self.get_guild_music(interaction.guild.id)
        queue = guild_music.queue

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("You're not in a voice channel.")
            return
        channel = interaction.user.voice.channel
        if not guild_music.vc or not guild_music.vc.is_connected():
            guild_music.vc = await channel.connect()

        # Extract info
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

        if 'entries' in info:
            for entry in info['entries']:
                queue.append(TrackInfo(url=entry['webpage_url'], title=entry.get('title', entry['url']),
                                            stream_url=entry['url']))
        else:
            queue.append(TrackInfo(url=info['webpage_url'], title=info.get('title', url), stream_url=info['url']))

        await interaction.followup.send(f"Added to queue: {info.get('title', url)}")

        # If nothing is playing, start playback
        if not guild_music.vc.is_playing() and not guild_music.vc.is_paused():
            await self._play_current(interaction)

    async def toggle_loop_queue(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        guild_music.loop_queue = not getattr(guild_music, 'loop_queue', False)
        state = "enabled" if guild_music.loop_queue else "disabled"
        await interaction.followup.send(f"Loop Queue {state}")

    async def _play_current(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        track = guild_music.queue[guild_music.current_index]

        if guild_music.vc.is_playing() or guild_music.vc.is_paused():
            guild_music.vc.stop()
            await asyncio.sleep(0.5)

        source = discord.FFmpegPCMAudio(track.stream_url, **self.FFMPEG_OPTIONS)
        guild_music.vc.play(source, after=lambda e: self.bot.loop.create_task(self._after_track(interaction)))

        embed = discord.Embed(title="Now Playing", description=track.title)
        view = PlayerView(self)
        await interaction.followup.send(embed=embed, view=view)

    async def _after_track(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if self.skip_flag:
            self.skip_flag = False
            return

        if getattr(guild_music, 'random_mode', False):
            guild_music.current_index = random.randint(0, len(guild_music.queue) - 1)
        elif guild_music.current_index + 1 < len(guild_music.queue):
            guild_music.current_index += 1
        else:
            if getattr(guild_music, 'loop_queue', False):
                guild_music.current_index = 0
            elif guild_music.loop247:
                random.shuffle(guild_music.queue)
                guild_music.current_index = 0
            else:
                return
        await self._play_current(interaction)

    async def stop(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if guild_music.vc:
            guild_music.vc.stop()
            guild_music.queue.clear()
            guild_music.current_index = 0
            await interaction.followup.send("Stopped playback.")

    async def pause(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if guild_music.vc and guild_music.vc.is_playing():
            guild_music.vc.pause()
            await interaction.followup.send("Paused.")
        elif guild_music.vc and guild_music.vc.is_paused():
            guild_music.vc.resume()
            await interaction.followup.send("Resumed.")
        else:
            await interaction.followup.send("Nothing to pause or resume.")

    async def next(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if getattr(guild_music, 'random_mode', False):
            guild_music.current_index = random.randint(0, len(guild_music.queue) - 1)
        elif guild_music.current_index + 1 < len(guild_music.queue):
            guild_music.current_index += 1
        else:
            if getattr(guild_music, 'loop_queue', False):
                guild_music.current_index = 0
            elif guild_music.loop247:
                random.shuffle(guild_music.queue)
                guild_music.current_index = 0
            else:
                return

        self.skip_flag = True
        guild_music.vc.stop()
        await asyncio.sleep(0.5)
        await self._play_current(interaction)

    async def previous(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if getattr(guild_music, 'random_mode', False):
            guild_music.current_index = random.randint(0, len(guild_music.queue) - 1)
        elif guild_music.current_index - 1 < 0:
            guild_music.current_index -= 1
        else:
            if getattr(guild_music, 'loop_queue', False):
                guild_music.current_index = 0
            elif guild_music.loop247:
                random.shuffle(guild_music.queue)
                guild_music.current_index = 0
            else:
                return

        guild_music.vc.stop()
        await self._play_current(interaction)

    async def toggle_247(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        guild_music.loop247 = not guild_music.loop247
        state = "enabled" if guild_music.loop247 else "disabled"
        await interaction.followup.send(f"24/7 mode {state}")

    # New: Shuffle the entire queue and restart playback
    async def shuffle(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        guild_music.random_mode = not getattr(guild_music, 'random_mode', False)
        state = "enabled" if guild_music.random_mode else "disabled"
        await interaction.followup.send(f"Random mode {state}")

    # New: Show full queue list
    async def show_queue(self, interaction: discord.Interaction):
        guild_music = self.get_guild_music(interaction.guild.id)
        if not guild_music.queue:
            await interaction.followup.send("Queue is empty.")
            return

        lines = []
        for idx, track in enumerate(guild_music.queue):
            prefix = '▶️' if idx == guild_music.current_index else f'{idx + 1}.'
            lines.append(f"{prefix} {track.title}")

            msg = "\n".join(lines)
            await interaction.followup.send(f"**Current Queue:**\n{msg}")


# View Buttons
class PlayerView(discord.ui.View):
    def __init__(self, controller: MusicController):
        super().__init__(timeout=None)
        self.controller = controller


    @discord.ui.button(label="⏮️ Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.controller.previous(interaction)

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.controller.stop(interaction)

    @discord.ui.button(label="⏯️ Pause/Resume", style=discord.ButtonStyle.secondary)
    async def pause_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.controller.pause(interaction)

    @discord.ui.button(label="⏭️ Next", style=discord.ButtonStyle.primary)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.controller.next(interaction)
