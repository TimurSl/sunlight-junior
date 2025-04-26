import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv
import os
load_dotenv()

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 2342413423243423
        self.total_channel_id = int(os.getenv("DISCORD_STATS_TOTAL_CHANNEL_ID"))
        self.humans_channel_id = int(os.getenv("DISCORD_STATS_HUMAN_CHANNEL_ID"))
        self.bots_channel_id = int(os.getenv("DISCORD_STATS_BOT_CHANNEL_ID"))
        self.update_stats.start()

    @tasks.loop(minutes=1)
    async def update_stats(self):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return

        total_members = guild.member_count
        humans = sum(1 for m in guild.members if not m.bot)
        bots = sum(1 for m in guild.members if m.bot)

        total_channel = guild.get_channel(self.total_channel_id)
        humans_channel = guild.get_channel(self.humans_channel_id)
        bots_channel = guild.get_channel(self.bots_channel_id)

        if total_channel:
            await total_channel.edit(name=f"📈 All Members: {total_members}")
        if humans_channel:
            await humans_channel.edit(name=f"👤 Humans: {humans}")
        if bots_channel:
            await bots_channel.edit(name=f"🤖 Bots: {bots}")

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

