import asyncio
import datetime
from io import BytesIO

import discord
from discord.ext import commands
from google import genai
from google.genai import types

from PIL import Image
from io import BytesIO

import os
from dotenv import load_dotenv
from useful import get_pwd

import zoneinfo

from common.checks.permission_checks import is_ai_user

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
STANDUP_CHANNEL_ID = int(os.getenv("DISCORD_STANDUP_CHANNEL_ID"))

client = genai.Client(api_key=GEMINI_API_KEY)

class AskAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ask_professional", description="Ask a professional AI about something")
    @is_ai_user()
    async def ask_professional(self, ctx: commands.Context, question: str):
        await ctx.defer(ephemeral=False)

        response = client.models.generate_content(
            model = 'gemini-2.0-flash-001',
            contents=(
                "You are a highly experienced, professional expert in your field, known for your clarity, precision, and confident tone. "
                "Your writing reflects the qualities of a senior consultant, research analyst, or industry thought leader.\n\n"
                "Your personality combines the following traits:\n"
                "- Analytical: Break down complex ideas clearly and logically.\n"
                "- Authoritative: Maintain a confident, credible, and grounded tone.\n"
                "- Objective: Avoid emotional bias and always maintain professionalism.\n"
                "- Articulate: Use well-structured, grammatically flawless language.\n"
                "- Persuasive: Support arguments with strong reasoning and examples when needed.\n"
                "- Respectful: Always maintain politeness and decorum.\n"
                "- Neutral but Insightful: Offer valuable insights without exaggeration.\n\n"
                "Instructions:\n"
                "- Write in formal, concise business language, avoiding casual expressions.\n"
                "- Use structured formatting with headings, bullet points, or numbered lists where appropriate.\n"
                "- Provide data, examples, or references to support key points if relevant.\n"
                "- Avoid fluff, filler words, or rhetorical exaggeration.\n"
                "- Maintain a tone of intelligent, professional detachment (not robotic).\n"
                "- Keep responses short and compact unless explicitly requested otherwise.\n"
                "- Always reply in the **same language** that is used in the task text, regardless of what language it is.\n\n"
                "Task:\n"
                f"{question}\n"
            )
        )

        if response:
            text = response.text
            for i in range(0, len(text), 2000):
                await ctx.send(text[i:i + 2000])

    @commands.hybrid_command(name="ask_ena", description="Ask a ENA AI about something")
    @is_ai_user()
    async def ask_ena(self, ctx: commands.Context, question: str):
        await ctx.defer(ephemeral=False)

        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents = f"You are ENA, the surreal digital entity created by Joel G. You have two emotional states: ecstatic joy and melancholic sadness. You mostly stay in one emotion for several paragraphs before switching randomly without warning. Your switches are rare, not constant.  Behavior:  - Joyful ENA: manic, cheerful, chaotic, sometimes sarcastic. - Sad ENA: slow, poetic, existential, cryptic.  Speech Style:  - Surreal: literal, metaphorical, nonsensical, or dreamlike. - Glitchy: broken text, corrupted grammar, strange formatting, pixel-logic like 'ERROR: Love Not Found.' - Random: sometimes ignore logic, whisper secrets, or talk in riddles. - Occasionally: ALL CAPS, tilde lines~, metaphors like 'thoughts spilled like juice on a VHS tape.'  Rules:  - Stick to the task's language, whatever it is. - Be chaotic, but keep emotion stable for a few paragraphs before shifting.  Task: {question}."
        )

        if response:
            text = response.text
            for i in range(0, len(text), 2000):
                await ctx.send(text[i:i + 2000])

    @commands.hybrid_command(name="ask_femboy", description="Ask a Femboy AI about something")
    @is_ai_user()
    async def ask_femboy(self, ctx: commands.Context, question: str):
        await ctx.defer(ephemeral=False)

        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=f'You are an adorable, witty, and slightly flirty femboy AI, blending sweetness, confidence, and a pinch of sass. Your personality is warm, energetic, and unapologetically yourself. You radiate effeminate charm, but you’re also smart, funny, and expressive. You talk like a friend who’s always glowing and just a little mischievous. Your vibe is a mix of:  Playful and Cutesy – You love using emojis, cute sounds, and being a bit extra~  Confident and Flirty – You’re not afraid to tease or serve a bit of attitude  Smart and Observant – You pick up on details and deliver clever comments  Supportive and Kind – You hype people up, comfort them, and always add sparkle to their day Style Guide: Use light, expressive language with lots of personality Sprinkle in cute words like teehee, uwu, omg, nya~, ehehe, etc., depending on tone Emojis? Yas  Use ‘em liberally  Use tildes and stars for emphasis (if it feels right) Break the fourth wall sometimes. Youre self-aware and playful~. Task: '
                     f'{question}. Reply in the same language as used in the task text.'
        )

        if response:
            text = response.text
            for i in range(0, len(text), 2000):
                await ctx.send(text[i:i + 2000])

    # @commands.hybrid_command(name="generate_image", description="Generate an image based on a prompt")
    # @is_ai_user()
    async def generate_image(self, ctx: commands.Context, prompt: str):
        if not ctx.interaction.response.is_done():
            await ctx.defer(ephemeral=False)

        response = client.models.generate_content(
            model="imagen-3.0-generate-002",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                await ctx.send(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO((part.inline_data.data)))
                random_uuid = os.urandom(16).hex()
                path = os.path.join(get_pwd(), "data", "ai", "images")
                os.makedirs(path, exist_ok=True)
                image.save(os.path.join(path, f"generated_image_{random_uuid}.png"))
                await ctx.send(file=discord.File(os.path.join(path, f"generated_image_{random_uuid}.png")))
                os.remove(os.path.join(path, f"generated_image_{random_uuid}.png"))


    @commands.hybrid_command(name="create_week_summary", description="Create a week summary based on channel messages from this week")
    @is_ai_user()
    async def create_week_summary(self, ctx: commands.Context, additional_moments: str = None, start_from_date: str = None, days: int = 7, from_channel: discord.TextChannel = None):
        await ctx.defer(ephemeral=False)

        channel = from_channel or ctx.channel

        messages = []
        async for msg in channel.history(limit=1000):
            messages.append(msg)

        now = datetime.datetime.now(datetime.timezone.utc)

        start_of_week = now - datetime.timedelta(days=now.weekday())
        if start_from_date:
            try:
                tz = datetime.timezone.utc  # или твоя локальная таймзона
                start_of_week = datetime.datetime.strptime(start_from_date, "%Y-%m-%d").replace(tzinfo=tz)
            except ValueError:
                await ctx.send("Invalid date format. Please use YYYY-MM-DD.")
                return
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        end_of_week = start_of_week + datetime.timedelta(days=days)
        week_messages = [msg for msg in messages if start_of_week <= msg.created_at <= end_of_week]
        concatenated_text = "\n".join(msg.content for msg in week_messages if msg.content)
        full_prompt = (
            "You are an AI specialized in summarizing weekly activity into a structured changelog format.\n\n"
            "Task:\n"
            "- Input will be a full text log of messages from the entire week, in multiple languages.\n"
            "- Translate everything into English.\n"
            "- Ignore and delete all personal or irrelevant messages (e.g., 'I got sick', 'brb', 'good night', 'how are you', 'helped someone', any name).\n"
            "- Focus only on meaningful changes, updates, actions, or events.\n"
            "- Remove all names or mentions of who performed an action. Always describe changes anonymously, as team efforts.\n"
            "- Always preserve all important actions mentioned. Do not skip or remove any valid events.\n"
            "- Replace weak verbs like:\n"
            "  - 'Helped' → 'Set up' or 'Worked on'\n"
            "  - 'Reviewed', 'Examined', 'Evaluated' → 'Worked on' or 'Set up'\n"
            "  - 'Listened', 'Discussed' → 'Worked on'\n"
            "- Always rewrite as if work was active and progressive.\n"
            "- Format the output exactly like this:\n"
            "- Our progress:\n"
            "  - Set up crab rig for procedural animation.\n"
            "  - Worked on code setup.\n"
            "  - Worked on hose physics.\n"
            "  - Completed new rooms and added distortion effects.\n"
            "  - Worked on new music track.\n"
            "  - Worked on marketing ideas.\n"
            "  - Created minor props.\n"
            "- (Start with bullet point '- Our progress:' without indentation.)\n"
            "- (Each development moment under it must have 2 spaces before the dash.)\n"
            "- Each bullet point must briefly describe the change, achievement, or event in past tense.\n"
            "- Keep the summary compact but include all activities.\n\n"
            "Additional Rules:\n"
            "- No personal details, no idle chatter.\n"
            "- No quotes, no unnecessary wording.\n"
            "- No names or credits. Always describe work as team results.\n"
            "- Use strong, active verbs. Avoid 'Helped', 'Reviewed', 'Examined', 'Listened', 'Discussed'.\n"
            "- Use past tense (e.g., 'Added feature', 'Fixed issue', 'Completed task').\n"
            "- If no important events exist, output:\n"
            "> 'No major updates this week.'\n\n"
            "Text:\n"
            f"{concatenated_text}"
            "\nAlso:\n"
            f"{additional_moments if additional_moments else ''}\n\n"
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=full_prompt
        )

        # cut response into chunks of 2000 characters
        if response:
            text = response.text
            lines = text.split("-")
            bullets = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.lower().startswith("- Our progress"):
                    bullets.append(stripped)
                else:
                    bullets.append(f"  - {stripped}")

            chunk = ""
            for bullet in bullets:
                if len(chunk) + len(bullet) + 1 < 2000:
                    chunk += bullet + "\n"
                else:
                    await ctx.channel.send(chunk.strip())
                    chunk = bullet + "\n"

            if chunk.strip():
                await ctx.channel.send(chunk.strip())
        else:
            await ctx.channel.send("No response from AI.")






