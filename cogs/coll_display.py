import discord
from discord.ext import commands
from discord import app_commands
import json
import os

TRADABLE_FILE = "tradablecoll.json"
RESTRICTED_FILE = "restrictedcoll.json"
ALLOWED_USER_ID = 941902212303556618  # Replace this with your ID

class CollDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_json(self, path):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def is_allowed_user(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == ALLOWED_USER_ID

    @app_commands.command(name="tradablecoll", description="View all tradable collectibles")
    async def tradablecoll(self, interaction: discord.Interaction):
        if not self.is_allowed_user(interaction):
            return await interaction.response.send_message("<:ap_crossmark:1382760353904988230> You are not allowed to use this command.", ephemeral=True)

        data = self.load_json(TRADABLE_FILE)

        embed = discord.Embed(
            title="📦 Tradable Collectibles",
            color=0x90ee90
        )

        if not data:
            embed.description = "No tradable collectibles found."
        else:
            for key, item in data.items():
                emoji = item.get("emoji", "❓")
                name = item.get("name", key)
                embed.add_field(name=name, value=emoji, inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ownercoll", description="View all restricted (owner-only) collectibles")
    async def ownercoll(self, interaction: discord.Interaction):
        if not self.is_allowed_user(interaction):
            return await interaction.response.send_message("<:ap_crossmark:1382760353904988230> You are not allowed to use this command.", ephemeral=True)

        data = self.load_json(RESTRICTED_FILE)

        embed = discord.Embed(
            title="🔒 Owner-Only Collectibles",
            color=0xffcccb
        )

        if not data:
            embed.description = "No restricted collectibles found."
        else:
            for key, item in data.items():
                emoji = item.get("emoji", "❓")
                name = item.get("name", key)
                owner_id = item.get("owner_id", 0)
                user = self.bot.get_user(owner_id)
                username = user.name if user else "Unknown User"
                mention = f"<@{owner_id}> ({username})"
                embed.add_field(name=name, value=f"{emoji} • {mention}", inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CollDisplay(bot))
