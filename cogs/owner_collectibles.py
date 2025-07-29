import discord
from discord.ext import commands
import json
import os
import time

COLL_FILE = "collectibles.json"
RESTRICTED_COLL_FILE = "restrictedcoll.json"
POINTS_FILE = "points.json"
USER_COOLDOWNS = {}  # Stores cooldowns in the format: {"user_id:coll": timestamp}

def load_restricted_colls():
    if not os.path.exists(RESTRICTED_COLL_FILE):
        with open(RESTRICTED_COLL_FILE, "w") as f:
            json.dump({}, f)
    with open(RESTRICTED_COLL_FILE, "r") as f:
        return json.load(f)

def get_data():
    if not os.path.exists(COLL_FILE):
        with open(COLL_FILE, "w") as f:
            json.dump({}, f)
    with open(COLL_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(COLL_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_points():
    if not os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "w") as f:
            json.dump({}, f)
    with open(POINTS_FILE, "r") as f:
        return json.load(f)

def save_points(points):
    with open(POINTS_FILE, "w") as f:
        json.dump(points, f, indent=4)

class RestrictedCollectibles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.restricted_colls = load_restricted_colls()

        for coll in self.restricted_colls:
            self.bot.add_command(self._create_command(coll))

    def ensure_user(self, data, user_id):
        if str(user_id) not in data:
            data[str(user_id)] = {c: 0 for c in self.restricted_colls}
        else:
            for c in self.restricted_colls:
                if c not in data[str(user_id)]:
                    data[str(user_id)][c] = 0
        return data

    def ensure_points_user(self, points, user_id):
        if str(user_id) not in points:
            points[str(user_id)] = 0
        return points

    async def send_restricted_coll(self, ctx, collectible, target: discord.Member):
        sender = ctx.author
        if sender.id == target.id:
            return await ctx.reply("You can't send collectibles to yourself!", delete_after=3)

        if collectible not in self.restricted_colls:
            return await ctx.reply("Unknown collectible!", delete_after=3)

        owner_id = int(self.restricted_colls[collectible]["owner_id"])
        if sender.id != owner_id:
            return await ctx.reply(
                f"**🚫 | {sender.name}**, only the owner of this collectible can send {collectible}s!",
                delete_after=3
            )

        cooldown_duration = self.restricted_colls[collectible].get("cooldown", 0)
        key = f"{sender.id}:{collectible}"
        now = int(time.time())
        if key in USER_COOLDOWNS and now < USER_COOLDOWNS[key]:
            retry_after = USER_COOLDOWNS[key]
            return await ctx.reply(
                f"**⏱ | {sender.name}**! Slow down and try the command again **<t:{retry_after}:R>**",
                delete_after=retry_after - now
            )

        data = get_data()
        data = self.ensure_user(data, sender.id)
        data = self.ensure_user(data, target.id)

        if data[str(sender.id)][collectible] < 1:
            await ctx.reply(
                f"**<:ap_crossmark:1382760353904988230> | {sender.name}**, you do not have any {collectible}s! >:c",
                delete_after=3
            )
            return await ctx.message.delete(delay=3)

        # Duplication-style logic
        data[str(sender.id)][collectible] -= 1
        data[str(target.id)][collectible] += 2
        save_data(data)

        # Add 1 point to sender
        points = load_points()
        points = self.ensure_points_user(points, sender.id)
        points[str(sender.id)] += 1
        save_points(points)

        USER_COOLDOWNS[key] = now + cooldown_duration

        emoji = self.restricted_colls[collectible]["emoji"]
        name = self.restricted_colls[collectible]["name"]
        await ctx.send(f"{emoji} **| {sender.name}** sent **{target.name}** 2 {name}!")

    def _create_command(self, collectible_key):
        @commands.command(name=collectible_key)
        async def _command(ctx, target: discord.Member = None):
            sender = ctx.author
            data = get_data()
            data = self.ensure_user(data, sender.id)

            if target is None:
                amount = data[str(sender.id)].get(collectible_key, 0)
                emoji = self.restricted_colls[collectible_key]["emoji"]
                name = self.restricted_colls[collectible_key]["name"]
                return await ctx.reply(
                    f"{emoji} **| {sender.name}**, you currently have {amount} {name}!"
                )

            await self.send_restricted_coll(ctx, collectible_key, target)

        return _command

async def setup(bot):
    await bot.add_cog(RestrictedCollectibles(bot))
