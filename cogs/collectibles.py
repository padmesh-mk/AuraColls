import discord
from discord.ext import commands
import json
import os
import time

COLL_FILE = "collectibles.json"
TRADABLE_COLL_FILE = "tradablecoll.json"
USER_COOLDOWNS = {}  # Stores cooldowns in the format: {"user_id:coll": timestamp}
COLL_LOG_FILE = "coll_logs.json"
POINTS_FILE = "points.json"

def log_collectible(sender_id, sender_name, target_id, target_name, collectible):
    log_entry = {
        "from_id": sender_id,
        "from_name": sender_name,
        "to_id": target_id,
        "to_name": target_name,
        "collectible": collectible,
        "timestamp": int(time.time())
    }
    logs = []
    if os.path.exists(COLL_LOG_FILE):
        with open(COLL_LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append(log_entry)
    with open(COLL_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def load_tradable_colls():
    if not os.path.exists(TRADABLE_COLL_FILE):
        with open(TRADABLE_COLL_FILE, "w") as f:
            json.dump({}, f)
    with open(TRADABLE_COLL_FILE, "r") as f:
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

def add_point(user_id):
    try:
        with open(POINTS_FILE, "r") as f:
            points_data = json.load(f)
    except FileNotFoundError:
        points_data = {}

    points_data[str(user_id)] = points_data.get(str(user_id), 0) + 1

    with open(POINTS_FILE, "w") as f:
        json.dump(points_data, f, indent=4)

class Collectibles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tradable_colls = load_tradable_colls()

        for coll in self.tradable_colls:
            self.bot.add_command(self._create_command(coll))

    def ensure_user(self, data, user_id):
        if str(user_id) not in data:
            data[str(user_id)] = {c: 0 for c in self.tradable_colls}
        else:
            for c in self.tradable_colls:
                if c not in data[str(user_id)]:
                    data[str(user_id)][c] = 0
        return data

    async def send_collectible(self, ctx, collectible, target: discord.Member):
        sender = ctx.author
        if sender.id == target.id:
            return await ctx.reply("You can't send collectibles to yourself!", delete_after=3)

        if collectible not in self.tradable_colls:
            return await ctx.reply("Unknown collectible!", delete_after=3)

        cooldown_duration = self.tradable_colls[collectible].get("cooldown", 0)
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
            await ctx.reply(f"**<:ap_crossmark:1382760353904988230> | {sender.name}**, you do not have any {collectible}s! >:c", delete_after=3)
            return await ctx.message.delete(delay=3)

        data[str(sender.id)][collectible] -= 1
        data[str(target.id)][collectible] += 2
        save_data(data)

        USER_COOLDOWNS[key] = now + cooldown_duration

        log_collectible(sender.id, sender.name, target.id, target.name, collectible)
        add_point(sender.id)  # ➕ Add point to sender

        emoji = self.tradable_colls[collectible]["emoji"]
        name = self.tradable_colls[collectible]["name"]
        await ctx.send(f"{emoji} **| {sender.name}** sent **{target.name}** 2 {name}!")

    def _create_command(self, collectible_key):
        @commands.command(name=collectible_key)
        async def _command(ctx, target: discord.Member = None):
            sender = ctx.author
            data = get_data()
            data = self.ensure_user(data, sender.id)

            if target is None:
                amount = data[str(sender.id)].get(collectible_key, 0)
                emoji = self.tradable_colls[collectible_key]["emoji"]
                name = self.tradable_colls[collectible_key]["name"]
                return await ctx.reply(f"{emoji} **| {sender.name}**, you currently have {amount} {name}!")

            await self.send_collectible(ctx, collectible_key, target)

        return _command

async def setup(bot):
    await bot.add_cog(Collectibles(bot))
