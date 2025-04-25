import requests
import discord
import json
from discord.ext import commands


class RandomPicture(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="cat", description="Give me a random cat!")
    async def cat(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)

        # request a random cat https://cataas.com/cat?json=true
        url = "https://cataas.com/cat?json=true"
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            image_url = data["url"]
            embed = discord.Embed(title="A cat!")
            embed.set_image(url=image_url)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Awww sorry no cat for you :(")


    @commands.hybrid_command(name="dog", description="Give me a random dog!")
    async def dog(self, ctx: commands.Context):
        await ctx.defer(ephemeral=False)
        # request a random dog https://dog.ceo/dog-api/
        url = "https://dog.ceo/api/breeds/image/random"
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            image_url = data["message"]
            embed = discord.Embed(title="A dog!")
            embed.set_image(url=image_url)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Awww sorry no dog for you :(")

