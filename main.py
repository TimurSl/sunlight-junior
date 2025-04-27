import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from commands.useful.chat_cleaner import ChatCleaner
from commands.fun.random_picture import RandomPicture
from commands.ai.ask_a_bot import AskAI
from cogs.stats import ServerStats



load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True




class CustomBot(commands.Bot):
    async def setup_hook(self):

        await bot.add_cog(ChatCleaner(bot))
        await bot.add_cog(RandomPicture(bot))
        await bot.add_cog(AskAI(bot))
        await bot.add_cog(ServerStats(bot))

        print("Reloaded all modules & synced commands.")

bot = CustomBot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

bot.run(TOKEN)
