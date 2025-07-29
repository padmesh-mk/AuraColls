import discord
from discord.ext import commands
from votes import get_leaderboard, get_user_data

class VoteLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="votelb", description="Show the top voters leaderboard", aliases=["vote lb"])
    async def votelb(self, ctx):
        lb = get_leaderboard()
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
            title="<:ap_chart:1384942967642394654> Global Vote Leaderboard",
            color=0xFF6B6B
        )

        user_data = get_user_data(str(user.id))
        embed.description = f"{user.name}: `{user_data['votes']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            votes = info["votes"]
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{votes}` – {username}")

        embed.add_field(name="Top Voters", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")

        view = LeaderboardPaginator(self, leaderboard, page)

        if isinstance(ctx_or_interaction, commands.Context):
            await ctx_or_interaction.send(embed=embed, view=view)
        else:
            await ctx_or_interaction.followup.send(embed=embed, view=view, ephemeral=False)


class LeaderboardPaginator(discord.ui.View):
    def __init__(self, cog: VoteLeaderboard, leaderboard, current_page):
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
        user_data = get_user_data(str(user.id))

        embed = discord.Embed(
            title="<:ap_chart:1384942967642394654> Global Vote Leaderboard",
            color=discord.Color.orange()
        )
        embed.description = f"{user.name}: `{user_data['votes']}` | Rank: `#{user_data['rank']}`\n\n"

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(self.leaderboard[start:end], start=start + 1):
            emoji = emoji_map.get(idx, f"#{idx}")
            votes = info["votes"]
            member = self.cog.bot.get_user(int(user_id))
            username = member.name if member else f"{user_id}"
            leaderboard_lines.append(f"{emoji}  `{votes}` – {username}")

        embed.add_field(name="Top Voters", value="\n".join(leaderboard_lines), inline=False)
        embed.set_footer(text=f"Page {page+1}/{total_pages}")
        return embed


async def setup(bot):
    await bot.add_cog(VoteLeaderboard(bot))
