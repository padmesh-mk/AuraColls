import discord
from discord.ext import commands
from discord import app_commands
import json
import os

COLL_FILE = "collectibles.json"
INFO_FILE = "collectible_info.json"
TRADABLE_FILE = "tradablecoll.json"
RESTRICTED_FILE = "restrictedcoll.json"

def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f)
    with open(filename, "r") as f:
        return json.load(f)

class CollListView(discord.ui.View):
    def __init__(self, bot, user: discord.User, user_data, all_info, tradable, restricted, filter_type="All"):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.user_data = user_data
        self.all_info = all_info
        self.tradable = tradable
        self.restricted = restricted
        self.filter_type = filter_type
        self.page = 0
        self.per_page = 15
        self.options = ["All", "Owned", "Not Owned", "Tradable", "Owner-only"]

        self.add_item(CollFilterDropdown(self))
        self.add_item(CollPaginateButton(self, direction="backward"))
        self.add_item(CollPaginateButton(self, direction="forward"))

    def get_filtered(self):
        # All keys from combined info
        all_keys = self.all_info.keys()
        data = {}
        if self.filter_type == "Owned":
            data = {k: v for k, v in self.user_data.items() if v > 0}
        elif self.filter_type == "Not Owned":
            data = {k: 0 for k in all_keys if k not in self.user_data or self.user_data[k] == 0}
        elif self.filter_type == "Tradable":
            data = {k: self.user_data.get(k, 0) for k in self.tradable}
        elif self.filter_type == "Owner-only":
            data = {k: self.user_data.get(k, 0) for k in self.restricted}
        else:
            data = {k: self.user_data.get(k, 0) for k in all_keys}
        
        # Sort by count (descending)
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        return sorted_data

    def get_embed(self):
        data = self.get_filtered()
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        keys = list(sorted_data.keys())
        total_pages = max((len(keys) - 1) // self.per_page + 1, 1)
        start = self.page * self.per_page
        end = start + self.per_page
        sliced = keys[start:end]

        embed = discord.Embed(
            title=f"{self.user.display_name}'s Collectibles",
            color=0xFF6B6B
        )

        desc = ""
        for key in sliced:
            info = self.all_info.get(key, {})
            emoji = info.get("emoji", "❓")
            name = info.get("name", key)
            count = sorted_data.get(key, 0)
            desc += f"{emoji} **{name}**: `{count}`\n"

        if not desc:
            desc = "*No collectibles to display.*"

        embed.description = desc
        embed.set_footer(text=f"Sorted by: {self.filter_type} • Page {self.page + 1}/{total_pages}")
        return embed


class CollFilterDropdown(discord.ui.Select):
    def __init__(self, view: CollListView):
        options = [
            discord.SelectOption(label=label, value=label)
            for label in view.options
        ]
        super().__init__(placeholder="Filter collectibles...", options=options)
        self.view_ref = view

    async def callback(self, interaction: discord.Interaction):
        self.view_ref.filter_type = self.values[0]
        self.view_ref.page = 0
        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)

class CollPaginateButton(discord.ui.Button):
    def __init__(self, view: CollListView, direction: str):
        emoji = "<:ap_backward:1382775479202746378>" if direction == "backward" else "<:ap_forward:1382775383371419790>"
        super().__init__(style=discord.ButtonStyle.secondary, emoji=emoji)
        self.view_ref = view
        self.direction = direction

    async def callback(self, interaction: discord.Interaction):
        total = len(self.view_ref.get_filtered())
        max_page = max((total - 1) // self.view_ref.per_page, 0)

        if self.direction == "forward":
            if self.view_ref.page < max_page:
                self.view_ref.page += 1
        else:
            if self.view_ref.page > 0:
                self.view_ref.page -= 1

        await interaction.response.edit_message(embed=self.view_ref.get_embed(), view=self.view_ref)

class ListCollectibles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_all_info(self):
        info1 = load_json(INFO_FILE)
        info2 = load_json(TRADABLE_FILE)
        info3 = load_json(RESTRICTED_FILE)
        combined = {}
        for d in (info1, info2, info3):
            for k, v in d.items():
                if k not in combined:
                    combined[k] = v
        return combined

    def get_user_collectibles(self, user_id):
        data = load_json(COLL_FILE)
        return data.get(str(user_id), {})

    @commands.command(name="list")
    async def collist_prefix(self, ctx, *, user: discord.Member = None):
        member = user or ctx.author
        user_items = self.get_user_collectibles(member.id)
        view = CollListView(
            self.bot,
            member,
            user_items,
            self.get_all_info(),
            load_json(TRADABLE_FILE),
            load_json(RESTRICTED_FILE),
        )
        await ctx.send(embed=view.get_embed(), view=view)

    @app_commands.command(name="list", description="List all collectibles")
    async def collist_slash(self, interaction: discord.Interaction, user: discord.Member = None):
        member = user or interaction.user
        user_items = self.get_user_collectibles(member.id)
        view = CollListView(
            self.bot,
            member,
            user_items,
            self.get_all_info(),
            load_json(TRADABLE_FILE),
            load_json(RESTRICTED_FILE),
        )
        await interaction.response.send_message(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(ListCollectibles(bot))
