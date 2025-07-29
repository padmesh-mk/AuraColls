import discord
from discord.ext import commands, tasks
import itertools
import datetime

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()  # Track when bot started
        self.status_cycle = itertools.cycle(self.generate_status_messages())
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    def generate_status_messages(self):
        return [
            lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{self.get_formatted_members()} members in {self.get_formatted_servers()} servers"),
            lambda: discord.Activity(type=discord.ActivityType.listening, name="ahelp"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name="members trading colls"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name="members in support server")
        ]

    def get_formatted_members(self):
        return f"{sum(g.member_count for g in self.bot.guilds):,}"

    def get_formatted_servers(self):
        return f"{len(self.bot.guilds):,}"

    def get_ping(self):
        return round(self.bot.latency * 1000)

    def get_uptime(self):
        delta = datetime.datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    @tasks.loop(minutes=1)
    async def status_loop(self):
        status_fn = next(self.status_cycle)
        await self.bot.change_presence(activity=status_fn())

    @status_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def update_status(self):
        status_fn = next(self.status_cycle)
        await self.bot.change_presence(activity=status_fn())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_status()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.update_status()

async def setup(bot):
    await bot.add_cog(Status(bot))
