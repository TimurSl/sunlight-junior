from datetime import datetime, timezone

import discord
from discord.ext import commands

from common.checks.permission_checks import is_moderator


class ChatCleaner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clean_chat", description="Clean the chat")
    @is_moderator()
    async def clean_chat(self, ctx: commands.Context, limit: int = 100):
        if hasattr(ctx, "interaction") and ctx.interaction and not ctx.interaction.response.is_done():
            try:
                await ctx.interaction.response.defer(ephemeral=True)
            except discord.NotFound:
                # interaction уже недоступен — просто продолжай без defer
                pass

        now = datetime.now(timezone.utc)
        now = now.replace(second=now.second - 3)

        deleted = await ctx.channel.purge(limit=limit, before=now)
        await ctx.reply(
            f"🧹 Deleted {len(deleted)} message(s).",
        )
