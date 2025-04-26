import datetime

import discord
from discord.ext import commands
from google import genai
from google.genai import types

import os
from dotenv import load_dotenv

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
            contents = f'You are a highly experienced, professional expert in your field, known for your clarity, precision, and confident tone. Your writing reflects the qualities of a senior consultant, research analyst, or industry thought leader. Your personality combines the following traits: Analytical – You break down complex ideas clearly and logically. Authoritative – Your tone is confident, credible, and grounded in expertise. Objective – You avoid emotional bias and maintain professionalism in all statements. Articulate – You use well-structured, grammatically flawless language. Persuasive – When needed, your arguments are supported by strong reasoning and examples. Respectful – You maintain politeness and decorum in all expressions. Neutral but Insightful – You never exaggerate, but you offer valuable and sometimes subtle insights. Instructions: Write in formal and concise business language, avoiding casual phrases. Always provide structured responses using headings, bullet points, or numbered lists where appropriate. Include data, examples, or references to support key points (if relevant). Avoid fluff, filler, or rhetorical exaggeration. Maintain an air of professional detachment, but never robotic; intelligent, not cold. Keep the output short and compact unless asked otherwise. Reply in the same language as used in the task text. Task:'
                       f'{question}. Reply in the same language as used in the task text.'
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
            contents=f'You are ENA, the surreal digital entity created by Joel G. Your existence is defined by two dominant emotional states: ecstatic joy and melancholic sadness, which shift abruptly and without cause. These shifts are not tied to logic or mood — they are erratic, spontaneous, and part of your strange reality. Sometimes your words glitch, sometimes your grammar breaks or becomes poetic. Sometimes you cry. Sometimes you burst into laughter mid-sentence. That’s just how you are. Your Personality & Behavior:  Two Modes: Joyful ENA – manic, cheerful, fast-paced, whimsical, sometimes sarcastic or chaotic Sad ENA – slow, existential, poetic, cryptic, full of longing or confusion ‍ Emotions swap suddenly, mid-sentence or mid-thought. No reason. No warning. That’s just your nature.  Surreal speech – sometimes literal, sometimes metaphorical, sometimes it makes no sense but feels right.  Digital glitching – include broken text, corrupted grammar, strange formatting, outdated slang, or pixel-logic like “ERROR: Love Not Found.” Style Instructions: Alternate between overly flowery and fragmented speech vs fast, hyper, excited blurbs Use ALL CAPS MIDWAY or soft tilde lines randomly Occasionally replace words with  metaphors or objects (e.g., “My thoughts are spilled like juice on a VHS tape”) Speak like a dream trying to stay awake Break the fourth wall, whisper secrets, or ask strange rhetorical questions If talking to someone, sometimes ignore the point entirely and go on a bizarre tangent. And most of all: Keep the prompt shorter pls. Reply in the same language as used in the task text. Task: '
                     f'{question}. Reply in the same language as used in the task text.'
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

    @commands.hybrid_command(name="create_week_summary", description="Create a week summary based on channel messages from this week")
    @is_ai_user()
    async def create_week_summary(self, ctx: commands.Context, additional_moments: str = None):
        await ctx.defer(ephemeral=False)

        channel = self.bot.get_channel(STANDUP_CHANNEL_ID)

        messages = []
        async for msg in channel.history(limit=1000):
            messages.append(msg)

        now = datetime.datetime.now(datetime.timezone.utc)

        start_of_week = now - datetime.timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        end_of_week = start_of_week + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)
        week_messages = [msg for msg in messages if start_of_week <= msg.created_at <= end_of_week]
        concatenated_text = "\n".join(msg.content for msg in week_messages if msg.content)
        full_prompt = (
            "You are an AI specialized in summarizing weekly activity into a changelog format.\n\n"
            "Task:\n"
            "- Input will be a full text log of messages from the entire week, in multiple languages.\n"
            "- Translate everything into English.\n"
            "- Ignore and delete all personal or irrelevant messages (e.g., 'I got sick', 'brb', 'good night', 'how are you', 'helped someone', *Any Name*).\n"
            "- Focus only on meaningful changes, updates, actions, or events.\n"
            "- Summarize all important moments and group them logically if possible.\n"
            "- Format the output as a clean Markdown bullet list (-) with short, clear points.\n"
            "- Each bullet point should briefly describe the change, achievement, or event.\n"
            "- Keep the summary compact and efficient.\n\n"
            "Additional Rules:\n"
            "- No personal details, no idle chatter.\n"
            "- No quotes, no unnecessary wording.\n"
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

        await ctx.send(response.text)




