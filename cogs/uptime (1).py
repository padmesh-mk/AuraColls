import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
import psutil  # ✅ Required for RAM/CPU stats

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_uptime(self):
        now = datetime.now(timezone.utc)
        delta = now - self.bot.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"**{days}d {hours}h {minutes}m {seconds}s**"

    def get_usage(self):
        process = psutil.Process()
        ram = process.memory_info().rss / (1024 ** 2)  # in MB
        cpu = process.cpu_percent(interval=0.5)  # in %
        return round(ram, 2), round(cpu, 1)

    def build_embed(self):
        uptime = self.get_uptime()
        ram_usage, cpu_usage = self.get_usage()

        embed = discord.Embed(
            title="<a:ap_uptime:1382717912120430702> Bot Uptime",
            description=f"**The bot has been online for:** {uptime}",
            color=0xFF6B6B
        )
        embed.add_field(name="<:ap_ram:1382719771782549655> RAM Usage", value=f"{ram_usage} MB", inline=True)
        embed.add_field(name="<:ap_cpu:1382719965781819414> CPU Usage", value=f"{cpu_usage}%", inline=True)
        embed.set_footer(text="Uptime info")
        return embed

    @commands.command()
    async def uptime(self, ctx):
        """Shows how long the bot has been online."""
        embed = self.build_embed()
        await ctx.send(embed=embed)

    @app_commands.command(name="uptime", description="Check how long the bot has been online.")
    async def slash_uptime(self, interaction: discord.Interaction):
        embed = self.build_embed()
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    bot.start_time = getattr(bot, 'start_time', datetime.now(timezone.utc))
    await bot.add_cog(Uptime(bot))
