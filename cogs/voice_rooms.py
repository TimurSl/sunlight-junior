import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
CREATE_CHANNEL_ID = int(os.getenv("DISCORD_VOICE_ROOMS_CHANNEL_ID"))

class VoiceRooms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CREATE_CHANNEL_ID = CREATE_CHANNEL_ID  # твой id канала
        self.user_rooms = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Пользователь зашел в канал для создания комнаты
        if after.channel and after.channel.id == self.CREATE_CHANNEL_ID:
            guild = after.channel.guild
            category = after.channel.category

            temp_channel = await guild.create_voice_channel(
                name=f"{member.display_name}'s Room",
                category=category
            )
            await member.move_to(temp_channel)

            self.user_rooms[member.id] = temp_channel.id

        # Пользователь вышел из своей временной комнаты
        if before.channel:
            temp_channel_id = self.user_rooms.get(member.id)
            if before.channel.id == temp_channel_id:
                channel = before.channel
                if len(channel.members) == 0:
                    await channel.delete()
                    del self.user_rooms[member.id]

    @commands.hybrid_command(name="rename", description="Rename your voice room")
    async def rename_room(self, ctx, *, new_name: str):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            return await ctx.send("❌ You are not in a voice channel.")

        # Проверка: автор комнаты или админ
        if channel.id != self.user_rooms.get(ctx.author.id) and not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("❌ You are not the owner of the room.")

        await channel.edit(name=new_name)
        await ctx.send(f"✅ Room renamed to: {new_name}")

    # Команда закрыть комнату
    @commands.hybrid_command(name="closeroom", description="Close your voice room")
    async def close_room(self, ctx):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            return await ctx.send("❌ You are not in a voice channel.")

        if channel.id != self.user_rooms.get(ctx.author.id) and not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("❌ You are not the owner of the room.")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔒 Room closed.")

    # Команда открыть комнату
    @commands.hybrid_command(name="openroom", description="Open your voice room")
    async def open_room(self, ctx):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if not channel:
            return await ctx.send("❌ You are not in a voice channel.")

        if channel.id != self.user_rooms.get(ctx.author.id) and not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("❌ You are not the owner of the room.")

        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.connect = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send("🔓 Room opened.")
