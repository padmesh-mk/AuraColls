import discord
from discord.ext import commands
import json
import os

POINTS_FILE = "points.json"
POINTS_EMOJI = "<:ac_points:1399447842594230505>"  # Replace with your desired emoji

def get_points(user_id):
    if not os.path.exists(POINTS_FILE):
        return 0

    with open(POINTS_FILE, "r") as f:
        data = json.load(f)

    return data.get(str(user_id), 0)

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="points", description="Check your collectible points", aliases=["point"])
    async def points(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        points = get_points(user.id)

        if user.id == ctx.author.id:
            msg = f"{POINTS_EMOJI} **| {user.display_name}**, you currently have **__{points}__ points!**"
        else:
            msg = f"{POINTS_EMOJI} **| {user.display_name}**, currently have **__{points}__ points!**"

        await ctx.reply(msg)

async def setup(bot):
    await bot.add_cog(Points(bot))
