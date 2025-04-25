import discord
from discord.ext import commands

from common.checks.permission_checks import is_moderator


class ChatCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clean_chat", description="Clean the chat")
    @is_moderator()
    async def clean_chat(self, ctx: commands.Context, limit: int = 100):
        await ctx.defer(ephemeral=True)

        deleted = await ctx.channel.purge(limit=limit)
        await ctx.send(
            f"🧹 Deleted {len(deleted)} message(s).",
            ephemeral=True
        )
