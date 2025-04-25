import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

from api.google.get_events import unix_time
from handlers.calendar_handler import CalendarHandler

load_dotenv()
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_NOTIFICATION_CHANNEL_ID"))

class Notifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = CalendarHandler()
        self.notified = set()
        self.check_calendar_events.start()

    @tasks.loop(minutes=1)
    async def check_calendar_events(self):
        now = datetime.now(timezone.utc)
        events = self.calendar.get_upcoming_events(days=1)
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)

        for event in events:
            event_id = event['id']
            summary = event.get('summary', 'Untitled Event')
            description = event.get('description', 'No description provided')
            start_str = event['start'].get('dateTime', event['start'].get('date'))
            start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            unix_timestamp = int(start_time.timestamp())

            for label, delta in [('24h', timedelta(hours=24)), ('3h', timedelta(hours=3)), ('now', timedelta(0))]:
                notify_time = start_time - delta
                unix_timestamp = int(start_time.timestamp())
                key = event_id

                if now >= notify_time and key not in self.notified:
                    embed_notification = discord.Embed(
                        title=f"🔔 Upcoming Event: {summary}",
                        description=f"{description}\n\nEvent starts at: <t:{unix_timestamp}:F>",
                        color=discord.Color.blue()
                    )
                    await channel.send("@here", embed=embed_notification)
                    self.notified.add(key)
                    break

    @tasks.loop(minutes=1)
    async def poll_changes_check(self):
        changes = self.calendar.check_for_changes()

        if changes:
            channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
            for change_type, event in changes:
                if change_type == 'new':
                    embed_notification = discord.Embed(
                        title=f"🔔 New Event: {event['summary']}",
                        description=f"Event starts at: <t:{unix_time(event)}:F>",
                        color=discord.Color.green()
                    )
                    await channel.send("@here", embed=embed_notification)
                elif change_type == 'updated':
                    embed_notification = discord.Embed(
                        title=f"🔄 Updated Event: {event['summary']}",
                        description=f"Event starts at: <t:{unix_time(event)}:F>",
                        color=discord.Color.yellow()
                    )
                    await channel.send("@here", embed=embed_notification)
                elif change_type == 'deleted':
                    embed_notification = discord.Embed(
                        title=f"❌ Deleted Event: {event['id']}",
                        description="This event has been deleted.",
                        color=discord.Color.red()
                    )
                    await channel.send("@here", embed=embed_notification)

    @check_calendar_events.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)
        await channel.send("🔔 Notifier is now active! I will notify you about upcoming events.")
