import discord
from discord.ext import commands
from discord import app_commands
import datetime
import platform
import psutil

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.launch_time = datetime.datetime.utcnow()
        self.created_on = datetime.datetime(2024, 12, 12)

    def get_uptime(self):
        delta = datetime.datetime.utcnow() - self.launch_time
        return str(delta).split('.')[0]  # Trim microseconds

    def get_memory_usage(self):
        mem = psutil.Process().memory_info().rss / 1024 / 1024
        return f"{mem:.2f} MB"

    def build_embed(self):
        total_guilds = len(self.bot.guilds)
        total_users = sum(g.member_count or 0 for g in self.bot.guilds)
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="<a:ap_bot:1382718727568756857> AuraColls Bot Info",
            description=(
                "AuraColls is a unique bot where you can collect and trade collectibles with other members.\n\n"
				"<a:ap_arroworrange:1382746363208667146> Use `ahelp` or `/help` to get started!"
            ),
            color=0xFF6B6B,
            timestamp=datetime.datetime.utcnow()
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="✨ Key Features",
            value=(
                "<a:ap_arroworrange:1382746363208667146> View your collectibles, check the leaderboard, and grow your collection!\n"
                "<a:ap_arroworrange:1382746363208667146> Collectibles can be duplicated through trading with other members.\n"
                "<a:ap_arroworrange:1382746363208667146> Some collectibles are owner-only and can only be given by that specific collectible's owner."
            ),
            inline=False
        )

        embed.add_field(name="<:ap_forward:1382775383371419790> Ping", value=f"`{latency} ms`", inline=True)
        embed.add_field(name="<a:ap_uptime:1382717912120430702> Uptime", value=f"`{self.get_uptime()}`", inline=True)
        embed.add_field(name="<:ap_ram:1382719771782549655> Memory", value=f"`{self.get_memory_usage()}`", inline=True)

        embed.add_field(name="<:ap_server:1382719087221674115> Servers", value=f"`{total_guilds}`", inline=True)
        embed.add_field(name="<:ap_users:1382719320072650772> Users", value=f"`{total_users}`", inline=True)
        embed.add_field(name="<:ap_date:1382718456000024631> Created On", value=f"`{self.created_on.strftime('%d %B %Y')}`", inline=True)

        embed.add_field(
            name="<:ap_developer:1382719599283408916> Developer",
            value="<@941902212303556618>",
            inline=True
        )

        embed.set_footer(text="Thanks for using AuraColls!")

        return embed

    def get_view(self):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Invite AuraColls", url="https://discord.com/oauth2/authorize?client_id=1261363542867578910"))
        view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/becvfQ9fCr"))
        view.add_item(discord.ui.Button(label="Top.gg Profile", url="https://discord.gg/becvfQ9fCr"))
        view.add_item(discord.ui.Button(label="Terms of Service", url="https://www.termsfeed.com/live/24ce705f-6734-4237-881f-18d31fb526ea"))
        view.add_item(discord.ui.Button(label="Privacy Policy", url="https://www.termsfeed.com/live/eb76629d-fcc2-4c31-b72f-905b9ad42024"))
        return view

    @commands.command(name="botinfo")
    async def botinfo_prefix(self, ctx):
        """Shows info about AuraColls bot."""
        await ctx.send(embed=self.build_embed(), view=self.get_view())

    @app_commands.command(name="botinfo", description="Shows info about AuraColls bot.")
    async def botinfo_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=self.build_embed(), view=self.get_view())

async def setup(bot):
    await bot.add_cog(BotInfo(bot))
