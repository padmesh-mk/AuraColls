import discord
from discord.ext import commands
from discord import app_commands
import json
import datetime
import asyncio

from votes import get_user_data, update_user_vote
from vote_remind import add_to_reminder, is_on_cooldown

# 🔧 CONFIGURATION
PUBLIC_LOG_CHANNEL_ID = 1399256316370751488
PRIVATE_LOG_CHANNEL_ID = 1399256437875540118
ROLE_REWARD_ID = 1398017116359233647
VOTE_LINK = "http://www.patience-is-a-virtue.org/"
COLLECTIBLES_FILE = "collectibles.json"  # 🟩 Collectible file path

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vote", description="Vote for the bot and claim reward", aliases=["v"])
    async def vote(self, ctx):
        await self.handle_vote(ctx)

    @app_commands.command(name="v", description="Alias for /vote")
    async def slash_vote(self, interaction: discord.Interaction):
        await self.handle_vote(interaction)

    async def handle_vote(self, ctx_or_inter):
        user = ctx_or_inter.user if isinstance(ctx_or_inter, discord.Interaction) else ctx_or_inter.author
        user_id = str(user.id)

        user_data = get_user_data(user_id)
        last_vote_ts = user_data.get("last_vote", 0)
        total_votes = user_data.get("votes", 0)
        rank = user_data.get("rank", "N/A")

        last_vote = f"<t:{int(last_vote_ts)}:R>" if last_vote_ts else "Never"

        embed = discord.Embed(
            title="<a:ap_bot:1382718727568756857> Auracolls Voting",
            description=(
                f"- **Your last vote**: {last_vote}\n"
                f"- **Total votes**: `{total_votes}`\n"
                f"- **Rank**: `#{rank}`"
            ),
            color=0xFF6B6B
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.set_footer(text="Global leaderboard: avotelb")

        view = VoteView(self.bot, user)

        if isinstance(ctx_or_inter, commands.Context):
            await ctx_or_inter.send(embed=embed, view=view)
        else:
            await ctx_or_inter.response.send_message(embed=embed, view=view)


class VoteView(discord.ui.View):
    def __init__(self, bot, user):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.clicked_at = datetime.datetime.utcnow()

        self.add_item(discord.ui.Button(label="📥 Vote", style=discord.ButtonStyle.link, url=VOTE_LINK))

    @discord.ui.button(label="🎁 Claim Reward", style=discord.ButtonStyle.green, custom_id="claim_vote")
    async def claim_reward(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            return await interaction.response.send_message(
                "<:ap_crossmark:1382760353904988230> This command must be used **inside a server**, not in DMs!",
                ephemeral=True
            )

        if interaction.user != self.user:
            return await interaction.response.send_message("This is not your vote panel!", ephemeral=True)

        now = datetime.datetime.utcnow()
        delta = (now - self.clicked_at).total_seconds()

        if delta < 10:
            return await interaction.response.send_message(
                f"{interaction.user.mention}, please vote before claiming the reward!",
                ephemeral=True
            )

        if is_on_cooldown(str(interaction.user.id)):
            user_data = get_user_data(str(interaction.user.id))
            last_vote_ts = user_data.get("last_vote", 0)
            total_votes = user_data.get("votes", 0)
            rank = user_data.get("rank", "N/A")
            last_vote = f"<t:{int(last_vote_ts)}:R>" if last_vote_ts else "Never"

            embed = discord.Embed(
                title="<a:ap_bot:1382718727568756857> AuraColls Voting",
                description=(
                    f"- **Your last vote**: {last_vote}\n"
                    f"- **Total votes**: `{total_votes}`\n"
                    f"- **Rank**: `{rank}`"
                ),
                color=discord.Color.orange()
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Global leaderboard: avotelb")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return await interaction.followup.send(
                f"<:ap_crossmark:1382760353904988230> {interaction.user.mention}, you have already voted for us today! Try again in {last_vote}",
                ephemeral=True
            )

        update_user_vote(str(interaction.user.id))
        add_to_reminder(str(interaction.user.id))

        # 🟩 Add collectible "top" to collectibles.json
        user_id_str = str(interaction.user.id)
        collectible_name = "voter"
        collectible_amount = 1

        try:
            with open(COLLECTIBLES_FILE, "r") as f:
                collectible_data = json.load(f)
        except FileNotFoundError:
            collectible_data = {}

        if user_id_str not in collectible_data:
            collectible_data[user_id_str] = {}

        collectible_data[user_id_str][collectible_name] = (
            collectible_data[user_id_str].get(collectible_name, 0) + collectible_amount
        )

        with open(COLLECTIBLES_FILE, "w") as f:
            json.dump(collectible_data, f, indent=4)

        # ✅ Reward role
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        role = guild.get_role(ROLE_REWARD_ID)

        if member and role:
            await member.add_roles(role, reason="Voted for AuraColls (12-hour reward)")

            async def remove_role_later():
                await asyncio.sleep(12 * 60 * 60)
                try:
                    await member.remove_roles(role, reason="Vote reward expired (12-hour)")
                except Exception as e:
                    print(f"Failed to remove vote role: {e}")

            self.bot.loop.create_task(remove_role_later())

        # ✅ Logs
        user_data = get_user_data(str(interaction.user.id))
        total_votes = user_data.get("votes", 0)
        rank = user_data.get("rank", "N/A")

        public_log = self.bot.get_channel(PUBLIC_LOG_CHANNEL_ID)
        if public_log:
            embed = discord.Embed(
                title="<:ap_vote:1395506333834543144> New Vote!",
                description=f"{interaction.user.mention} just voted for **AuraColl** on [Top.gg]({VOTE_LINK})\n"
                            f"**Total Votes:** `{total_votes}`",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text="Thank you for supporting us!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await public_log.send(embed=embed)

        private_log = self.bot.get_channel(PRIVATE_LOG_CHANNEL_ID)
        if private_log:
            msg_id = interaction.message.id if interaction.message else "N/A"
            msg_link = f"https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{msg_id}"

            embed = discord.Embed(
                title="📬 New Vote Logged",
                color=discord.Color.dark_purple(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.add_field(name="User", value=f"{interaction.user.mention} (`{interaction.user.id}`)", inline=False)
            embed.add_field(name="Username", value=f"`{interaction.user.name}#{interaction.user.discriminator}`", inline=False)
            embed.add_field(name="Server", value=f"{interaction.guild.name} (`{interaction.guild_id}`)", inline=False)
            embed.add_field(name="Total Votes", value=f"`{total_votes}`", inline=True)
            embed.add_field(name="Rank", value=f"`#{rank}`", inline=True)
            embed.add_field(name="Message Link", value=f"[Jump to message]({msg_link})", inline=False)
            embed.set_footer(text="Private Vote Log")

            await private_log.send(embed=embed)

        # 🟩 Thank you message with collectible
        thank_embed = discord.Embed(
            description=(
                f"{interaction.user.mention}, thank you for voting! 🎉\n"
                f"You've received 1x <:ap_vote:1395506333834543144> **Voter** collectible!"
            ),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=thank_embed)


async def setup(bot):
    await bot.add_cog(Vote(bot))
