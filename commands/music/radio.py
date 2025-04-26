import discord
from discord.ext import commands
from discord import app_commands

class Radio(commands.Cog):
    def __init__(self, bot: commands.Bot, controller):
        self.bot = bot
        self.controller = controller

    @app_commands.command(name="radio", description="Toggle radio mode")
    async def radio(self, interaction: discord.Interaction):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        await self.controller.toggle_radio(interaction)
