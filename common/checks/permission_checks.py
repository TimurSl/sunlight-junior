from discord.ext import commands
from dotenv import load_dotenv
import os
load_dotenv()

MODERATOR_ROLE_ID = int(os.getenv("MODERATOR_ROLE_ID"))

def is_moderator():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return MODERATOR_ROLE_ID in [r.id for r in ctx.author.roles]
    return commands.check(predicate)

AI_USER_ROLE_ID = int(os.getenv("DISCORD_AI_USER_ROLE_ID"))

def is_ai_user():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        return AI_USER_ROLE_ID in [r.id for r in ctx.author.roles]
    return commands.check(predicate)
