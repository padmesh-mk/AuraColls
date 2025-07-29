import discord
from discord.ext import commands
from discord import app_commands
import random
import json
import os
from datetime import datetime, timedelta

DAILY_FILE = "daily.json"
POINTS_FILE = "points.json"
COLLECTIBLES_FILE = "collectibles.json"

COLLECTIBLES = ["Kubo", "Luma", "Bobo", "Nubi", "Roro"]
COLLECTIBLE_EMOJIS = {
    "Kubo": "<a:ac_vanillabearicecream:1399440453778280591>",
    "Luma": "<a:ac_bluebearicecream:1399440402255188120>",
    "Bobo": "<a:ac_chocolatebearicecream:1399440480332152922>",
    "Nubi": "<a:ac_pinkbearicecream:1399440514591490118>",
    "Roro": "<a:ac_redbearicecream:1399440427098308749>"
}

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def get_remaining_time():
    now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    next_reset = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now.hour >= 9:
        next_reset += timedelta(days=1)
    remaining = next_reset - now
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}H {minutes}M {seconds}S"

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def claim_daily(self, user: discord.User):
        user_id = str(user.id)

        daily_data = load_json(DAILY_FILE)
        points_data = load_json(POINTS_FILE)
        coll_data = load_json(COLLECTIBLES_FILE)

        now = datetime.utcnow() + timedelta(hours=5, minutes=30)

        last_claim = daily_data.get(user_id, {}).get("last_claim")
        streak = daily_data.get(user_id, {}).get("streak", 0)

        if last_claim:
            last_time = datetime.fromisoformat(last_claim)
            reset_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now.hour < 9:
                reset_time -= timedelta(days=1)
            if last_time >= reset_time:
                return False, streak, None, None, get_remaining_time()

        # Update streak and time
        streak += 1
        daily_data[user_id] = {
            "last_claim": now.isoformat(),
            "streak": streak
        }
        save_json(DAILY_FILE, daily_data)

        # Random points and collectible
        points = random.randint(1, 10)
        collectible = random.choice(COLLECTIBLES)

        # Update points
        points_data[user_id] = points_data.get(user_id, 0) + points
        save_json(POINTS_FILE, points_data)

        # Update collectible
        if user_id not in coll_data:
            coll_data[user_id] = {}
        coll_data[user_id][collectible] = coll_data[user_id].get(collectible, 0) + 1
        save_json(COLLECTIBLES_FILE, coll_data)

        return True, streak, points, collectible, None

    @commands.command(name="daily")
    async def daily_prefix(self, ctx):
        success, streak, points, collectible, remaining = await self.claim_daily(ctx.author)
        emoji = "🌟"
        user = ctx.author.name

        if success:
            coll_emoji = COLLECTIBLE_EMOJIS.get(collectible, "🎁")
            await ctx.reply(
                f"<:ac_points:1399447842594230505> **| {user}**, Here is your daily **{points} Points**!\n"
                f"<:ac_blank:1399434326591934515> **|** You're on a **{streak} daily streak**!\n"
                f"**{coll_emoji} |** You received a **{collectible}**!\n"
                f"**<:ap_time:1382729675616555029> |** Your next daily is in: **{get_remaining_time()}**",
                mention_author=False
            )
        else:
            await ctx.reply(
                f"<:ap_time:1382729675616555029> **| {user}**, you already claimed your daily!\n"
                f"Come back in: **{remaining}**",
                mention_author=False
            )

    @app_commands.command(name="daily", description="Claim your daily points and collectible")
    async def daily_slash(self, interaction: discord.Interaction):
        success, streak, points, collectible, remaining = await self.claim_daily(interaction.user)
        emoji = "🌟"
        user = interaction.user.name

        if success:
            coll_emoji = COLLECTIBLE_EMOJIS.get(collectible, "🎁")
            await interaction.response.send_message(
                f"<:ac_points:1399447842594230505> **| {user}**, Here is your daily **{points} Points**!\n"
                f"<:ac_blank:1399434326591934515> **|** You're on a **{streak} daily streak**!\n"
                f"**{coll_emoji} |** You received a **{collectible}**!\n"
                f"**<:ap_time:1382729675616555029> |** Your next daily is in: **{get_remaining_time()}**"
            )
        else:
            await interaction.response.send_message(
                f"<:ap_time:1382729675616555029> **| {user}**, you already claimed your daily!\n"
                f"Come back in: **{remaining}**"
            )

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.bot.tree.add_command(self.daily_slash)
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(Daily(bot))
