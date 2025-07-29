import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from votes import get_leaderboard

# 🔧 Set your target channel ID here
CHANNEL_ID = 1399253626798604338  # Replace with your channel ID

class VoteLeaderboardSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_today = False
        self.send_lb_daily.start()

    def cog_unload(self):
        self.send_lb_daily.cancel()

    @tasks.loop(minutes=1)
    async def send_lb_daily(self):
        now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # Convert to IST
        if now.hour == 9 and now.minute == 0 and not self.sent_today:
            await self.send_leaderboard()
            self.sent_today = True
        elif now.minute != 0:
            self.sent_today = False  # Reset once we're past the 9:00 minute

    async def send_leaderboard(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            print(f"[VoteLeaderboard] Channel with ID {CHANNEL_ID} not found.")
            return

        lb = get_leaderboard()
        if not lb:
            await channel.send("📛 No vote data available right now.")
            return

        embed = discord.Embed(
            title="<:ap_chart:1384942967642394654> Global Vote Leaderboard",
            color=0xFF6B6B
        )

        emoji_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        leaderboard_lines = []

        for idx, (user_id, info) in enumerate(lb[:10], start=1):
            emoji = emoji_map.get(idx, f"#{idx}")
            votes = info["votes"]
            member = self.bot.get_user(int(user_id))
            username = member.name if member else f"`{user_id}`"
            leaderboard_lines.append(f"{emoji}  `{votes}` – {username}")

        embed.add_field(name="Top 10 Voters", value="\n".join(leaderboard_lines), inline=False)

        # ⏰ Add IST timestamp
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        embed.set_footer(text=f"Last updated: {ist_now.strftime('%Y-%m-%d %I:%M %p IST')} • Next update in 24 hours")

        await channel.send(embed=embed)

    @send_lb_daily.before_loop
    async def before_leaderboard(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(VoteLeaderboardSender(bot))
