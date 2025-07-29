import discord
from discord.ext import commands
from discord import app_commands
import time
import random  # Replace with actual DB latency fetch if available

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_status_emoji(self, latency):
        if latency < 100:
            return "🟢 Excellent"
        elif latency < 200:
            return "🟡 Good"
        elif latency < 300:
            return "🟠 Moderate"
        else:
            return "🔴 Poor"

    async def build_ping_embed(self, ctx_or_interaction):
        start = time.perf_counter()
        if isinstance(ctx_or_interaction, commands.Context):
            message = await ctx_or_interaction.send("Measuring ping...")
        else:
            await ctx_or_interaction.response.defer()
            message = await ctx_or_interaction.followup.send("Measuring ping...", wait=True)
        end = time.perf_counter()

        websocket_latency = round(self.bot.latency * 1000, 2)
        api_latency = round((end - start) * 1000, 2)

        # Replace this with actual MongoDB latency if you have it
        mongo_latency = round(random.uniform(100, 200), 2)

        status = self.get_status_emoji(websocket_latency)

        embed = discord.Embed(
            title="<a:ap_uptime:1382717912120430702> Pong!",
            color=discord.Color.green()
        )
        embed.add_field(name="WebSocket Latency", value=f"`{websocket_latency}ms`", inline=True)
        embed.add_field(name="API Latency", value=f"`{api_latency}ms`", inline=True)
        embed.add_field(name="MongoDB Latency", value=f"`{mongo_latency}ms`", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.set_footer(text="Latency stats may vary slightly each time.")

        await message.edit(content=None, embed=embed)

    @commands.command(name="ping", help="Shows latency info")
    async def ping(self, ctx):
        await self.build_ping_embed(ctx)

    @app_commands.command(name="ping", description="Shows latency info")
    async def slash_ping(self, interaction: discord.Interaction):
        await self.build_ping_embed(interaction)

async def setup(bot):
    await bot.add_cog(Ping(bot))
