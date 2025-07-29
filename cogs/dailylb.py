import discord
from discord.ext import commands
import json
import os

DAILY_FILE = "daily.json"

def get_daily_leaderboard():
    if not os.path.exists(DAILY_FILE):
        return []

    with open(DAILY_FILE, "r") as f:
        data = json.load(f)

    sorted_data = sorted(data.items(), key=lambda x: x[1].get("streak", 0), reverse=True)
    leaderboard = []
    for user_id, info in sorted_data:
        leaderboard.append((user_id, {"streak": info.get("streak", 0)}))
    return leaderboard

def get_user_daily_data(user_id):
    leaderboard = get_daily_leaderboard()
    for rank, (uid, info) in enumerate(leaderboard, start=1):
        if str(uid) == str(user_id):
            return {"streak": info["streak"], "rank": rank}
    return {"streak": 0, "rank": "N/A"}

class DailyLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dailylb", description="Show the top daily claimers leaderboard", aliases=["daily lb"])
    async def dailylb(self, ctx):
        lb = get_daily_leaderboard()
        await self.show_page(ctx, lb, 0)

    async def show_page(self, ctx_or_interaction, leaderboard, page: int):
        PER_PAGE = 10
        total_pages = (len(leaderboard) + PER_PAGE - 1) // PER_PAGE
        page = max(0, min(page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        if isinstance(ctx_or_interaction, commands.Context):
            user = ctx_or_interaction.author
        else:
            user = ctx_or_interaction.user

        embed = discord.Embed(
            title="<:ap_daily:1395624067648720998> Global Daily Leaderboard",
            color=0xFF6B6B
        )

        user_data = get_user_daily_data(user.id)
        embed.description = f"{user.name}: `{user_data['streak']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            streak = info["streak"]
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{streak}` – {username}")

        embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = DailyLeaderboardPaginator(self, leaderboard, page)

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.followup.send(embed=embed, view=view, ephemeral=False)

class DailyLeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: DailyLeaderboard, leaderboard, current_page):
        super().__init__(timeout=60)
        self.cog = cog
        self.leaderboard = leaderboard
        self.page = current_page

    @discord.ui.button(emoji="<:ap_backward:1382775479202746378>", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = max(0, self.page - 1)
        await self.update(interaction)

    @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = min(self.page + 1, (len(self.leaderboard) + 9) // 10 - 1)
        await self.update(interaction)

    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = await self.build_embed(interaction)
        await interaction.message.edit(embed=embed, view=self)

    async def build_embed(self, interaction):
        PER_PAGE = 10
        total_pages = (len(self.leaderboard) + PER_PAGE - 1) // PER_PAGE
        page = max(0, min(self.page, total_pages - 1))
        start = page * PER_PAGE
        end = start + PER_PAGE

        user = interaction.user
        user_data = get_user_daily_data(user.id)

        embed = discord.Embed(
            title="<:ap_daily:1395624067648720998> Global Daily Leaderboard",
            color=discord.Color.orange()
        )
        embed.description = f"{user.name}: `{user_data['streak']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(self.leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            streak = info["streak"]
            member = self.cog.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{streak}` – {username}")

        embed.add_field(name="Top Daily Claimers", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed

async def setup(bot):
    await bot.add_cog(DailyLeaderboard(bot))
