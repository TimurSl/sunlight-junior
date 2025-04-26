import discord
from discord.ext import commands
import json
import os
import re
from useful import get_pwd

# Default empty config template
DEFAULT_CONFIG = {
    "MODERATOR_ROLE_ID": "",
    "GOOGLE_CLIENT_ID": "",
    "GOOGLE_CLIENT_SECRET": "",
    "GOOGLE_API_KEY": "",
    "GEMINI_API_KEY": "",
    "CALENDAR_ID": "",
    "DISCORD_NOTIFICATION_CHANNEL_ID": "",
    "DISCORD_STANDUP_CHANNEL_ID": "",
    "DISCORD_AI_USER_ROLE_ID": "",
    "DISCORD_MUSIC_ROLE_ID": "",
    "DISCORD_VOICE_ROOMS_CHANNEL_ID": "",
    "DISCORD_STATS_TOTAL_CHANNEL_ID": "",
    "DISCORD_STATS_HUMAN_CHANNEL_ID": "",
    "DISCORD_STATS_BOT_CHANNEL_ID": ""
}


class Configurator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_dir = os.path.join(get_pwd(), "data", "config")
        os.makedirs(self.config_dir, exist_ok=True)

    def get_config_path(self, guild_id):
        return os.path.join(self.config_dir, f"{guild_id}.json")

    def load_config(self, guild_id):
        path = self.get_config_path(guild_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        else:
            self.save_config(guild_id, DEFAULT_CONFIG.copy())
            return DEFAULT_CONFIG.copy()

    def save_config(self, guild_id, data):
        path = self.get_config_path(guild_id)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        config = self.load_config(guild.id)
        # Check for missing keys
        missing_keys = [key for key, value in config.items() if not value]

        owner = guild.owner
        if owner:
            try:
                message = (
                        f"👋 Hello, {owner.name}!\n"
                        f"The bot has joined your server **{guild.name}**.\n\n"
                        "🚧 Please configure the following parameters:\n"
                        + "\n".join(f"- {key}" for key in missing_keys) +
                        "\n\nUse the `/configure` command to set each parameter."
                )
                await owner.send(message)
            except discord.Forbidden:
                print(f"❌ Cannot send DM to the owner of {guild.name}")

    @commands.hybrid_command(name="configure", description="Set a configuration value for this server.")
    @commands.has_permissions(administrator=True)
    async def configure(self, ctx, key: str, value: str):
        guild_id = ctx.guild.id
        config = self.load_config(guild_id)

        if key not in config:
            return await ctx.send(f"❌ Invalid key. Available keys:\n" + ", ".join(config.keys()))

        # Detect if value is a role mention
        if re.match(r"<@&\d+>", value):
            role_id = int(re.findall(r"\d+", value)[0])
            config[key] = role_id
        # Detect if value is a channel mention
        elif re.match(r"<#\d+>", value):
            channel_id = int(re.findall(r"\d+", value)[0])
            config[key] = channel_id
        else:
            config[key] = value

        self.save_config(guild_id, config)
        await ctx.send(f"✅ Successfully set `{key}` to `{value}`.")

    @commands.hybrid_command(name="viewconfig", description="View the current configuration for this server.")
    @commands.has_permissions(administrator=True)
    async def view_config(self, ctx):
        guild_id = ctx.guild.id
        config = self.load_config(guild_id)

        if not config:
            return await ctx.send("❌ No configuration found for this server.")

        text = "\n".join([f"**{key}**: `{value}`" for key, value in config.items()])
        await ctx.send(f"📄 Current configuration:\n{text}")


async def setup(bot):
    await bot.add_cog(Configurator(bot))
