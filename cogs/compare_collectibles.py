import discord
from discord.ext import commands
from discord import app_commands
import json

with open("collectibles.json", "r") as f:
    user_collectibles = json.load(f)

with open("collectible_info.json", "r") as f:
    daily_info = json.load(f)

with open("restrictedcoll.json", "r") as f:
    restricted_info = json.load(f)

with open("tradablecoll.json", "r") as f:
    tradable_info = json.load(f)


def get_collectible_details(coll):
    for db in [daily_info, restricted_info, tradable_info]:
        if coll in db:
            return db[coll]
    return None


def get_user_counts(user_id):
    return user_collectibles.get(str(user_id), {})


def get_filtered_collectibles(user1, user2, filter_type):
    all_keys = set(daily_info.keys()) | set(restricted_info.keys()) | set(tradable_info.keys())
    result = []
    for coll in all_keys:
        count1 = user1.get(coll, 0)
        count2 = user2.get(coll, 0)
        if filter_type == "owned" and (count1 > 0 or count2 > 0):
            result.append(coll)
        elif filter_type == "not_owned" and count1 == 0 and count2 == 0:
            result.append(coll)
        elif filter_type == "tradable" and coll in tradable_info:
            result.append(coll)
        elif filter_type == "owner_only" and coll in restricted_info:
            result.append(coll)
        elif filter_type == "all":
            result.append(coll)
    return sorted(result, key=lambda x: user1.get(x, 0) + user2.get(x, 0), reverse=True)


class CompareDropdown(discord.ui.Select):
    def __init__(self, user1, user2, cog):
        self.user1 = user1
        self.user2 = user2
        self.cog = cog

        options = [
            discord.SelectOption(label="Owned", value="owned"),
            discord.SelectOption(label="Not Owned", value="not_owned"),
            discord.SelectOption(label="Tradable", value="tradable"),
            discord.SelectOption(label="Owner-only", value="owner_only"),
            discord.SelectOption(label="All", value="all"),
        ]
        super().__init__(placeholder="Choose a filter", options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.cog.send_compare_embed(interaction, self.user1, self.user2, 0, self.values[0])


class CompareView(discord.ui.View):
    def __init__(self, cog, user1, user2, index, filter_type):
        super().__init__(timeout=120)
        self.cog = cog
        self.user1 = user1
        self.user2 = user2
        self.index = index
        self.filter_type = filter_type

        self.add_item(CompareDropdown(user1, user2, cog))

    @discord.ui.button(emoji="<:ap_backward:1382775479202746378>", style=discord.ButtonStyle.blurple)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = max(self.index - 1, 0)
        await self.cog.send_compare_embed(interaction, self.user1, self.user2, self.index, self.filter_type)

    @discord.ui.button(emoji="<:ap_forward:1382775383371419790>", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index += 1
        await self.cog.send_compare_embed(interaction, self.user1, self.user2, self.index, self.filter_type)


class CompareCollectibles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_compare_embed(self, interaction, user1, user2, page, filter_type):
        data1 = get_user_counts(user1.id)
        data2 = get_user_counts(user2.id)

        filtered = get_filtered_collectibles(data1, data2, filter_type)
        per_page = 15
        max_page = max((len(filtered) - 1) // per_page, 0)
        page = max(0, min(page, max_page))
        items = filtered[page * per_page:(page + 1) * per_page]

        description = ""
        for item in items:
            details = get_collectible_details(item)
            emoji = details.get("emoji", "") if details else ""
            count1 = data1.get(item, 0)
            count2 = data2.get(item, 0)
            description += f"{emoji} **{item}**: `{count1}` vs `{count2}`\n"

        if not description:
            description = "No collectibles found for this filter."

        embed = discord.Embed(
            title=f"Collectible Comparison: {user1.name} vs {user2.name}",
            description=description,
            color=discord.Color.red()
        )

        embed.set_footer(text=f"Sorted by: {filter_type.replace('_', ' ').title()} • Page {page + 1}/{max_page + 1}")
        view = CompareView(self, user1, user2, page, filter_type)

        if isinstance(interaction, discord.Interaction):
            if not interaction.response.is_done():
                await interaction.response.defer()
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.message.edit(embed=embed, view=view)

    @app_commands.command(name="compare", description="Compare collectibles with another user.")
    async def compare_slash(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message("Loading comparison...", ephemeral=True)
        await self.send_compare_embed(interaction, interaction.user, member, 0, "owned")

    @commands.command(name="compare")
    async def compare_prefix(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.send("Mention a user to compare with.")

        class SimpleInteraction:
            def __init__(self, ctx):
                self.ctx = ctx
                self.user = ctx.author
                self._message = None

            @property
            def message(self):
                return self._message

            async def edit_original_response(self, **kwargs):
                if self._message:
                    await self._message.edit(**kwargs)
                else:
                    self._message = await self.ctx.send(**kwargs)

        interaction = SimpleInteraction(ctx)
        interaction._message = await ctx.send("Loading comparison...")
        await self.send_compare_embed(interaction, ctx.author, member, 0, "owned")


async def setup(bot):
    await bot.add_cog(CompareCollectibles(bot))
