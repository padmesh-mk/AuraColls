import discord
from discord.ext import commands

LOG_CHANNEL_ID = 1398017169375101088  # Replace with your actual log channel ID

class GuildLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            owner = await self.bot.fetch_user(guild.owner_id)
            owner_text = f"{owner} (`{owner.id}`)"

            # DM the server owner
            try:
                dm_embed = discord.Embed(
                    title=f"<a:ap_bot:1382718727568756857> Thanks for Adding {self.bot.user.name}!",
                    description=(
                        f"Hey **{owner.name}**, thanks for adding me to **{guild.name}**!\n"
						"<:ap_developer:1382719599283408916> Developer: <@941902212303556618> `bmtamilgaming_yt` \n\n"
                        "Here’s some helpful info to get started:"
                    ),
                    color=0xff7800  # Orange color
                )
                dm_embed.add_field(name="<a:ap_arroworange:1382746363208667146> Help Command", value="Use `ahelp` to view all commands.", inline=False)
                dm_embed.add_field(name="<:ap_support:1382716862256910437> Support Server", value="[Join Support Server](https://discord.gg/becvfQ9fCr)", inline=False)
                dm_embed.add_field(name="<:ap_invite:1382717191052328961> Invite the Bot", value="[Click Here](https://discord.com/oauth2/authorize?client_id=1261363542867578910)", inline=False)
                dm_embed.add_field(name="📄 Terms & Conditions", value="[View Terms](https://www.termsfeed.com/live/24ce705f-6734-4237-881f-18d31fb526ea)", inline=False)
                dm_embed.add_field(name="🔐 Privacy Policy", value="[View Privacy Policy](https://www.termsfeed.com/live/eb76629d-fcc2-4c31-b72f-905b9ad42024)", inline=False)
                dm_embed.set_footer(text="Happy to be in your server!")

                await owner.send(embed=dm_embed)
            except discord.Forbidden:
                print(f"Couldn't DM the owner of {guild.name}.")

        except discord.HTTPException:
            owner_text = f"Unknown (`{guild.owner_id}`)"

        # Log to log channel
        embed = discord.Embed(
            title="📥 Joined a New Server!",
            description=f"**Server Name:** {guild.name}\n**Members:** {guild.member_count}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=False)
        embed.add_field(name="👑 Owner", value=owner_text, inline=False)
        embed.add_field(name="📅 Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="📊 Total Servers", value=str(len(self.bot.guilds)), inline=False)
        embed.set_footer(text="Server Joined")

        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            owner = await self.bot.fetch_user(guild.owner_id)
            owner_text = f"{owner} (`{owner.id}`)"
        except discord.HTTPException:
            owner_text = f"Unknown (`{guild.owner_id}`)"

        embed = discord.Embed(
            title="📤 Removed from a Server",
            description=f"**Server Name:** {guild.name}\n**Members at Leave:** {guild.member_count}",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=False)
        embed.add_field(name="👑 Owner", value=owner_text, inline=False)
        embed.add_field(name="📅 Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
        embed.add_field(name="📊 Total Servers", value=str(len(self.bot.guilds)), inline=False)
        embed.set_footer(text="Server Left")

        await self.send_log(embed)

    async def send_log(self, embed):
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                print("❌ Missing permission to send log message.")
        else:
            print("❌ Log channel not found.")

async def setup(bot):
    await bot.add_cog(GuildLogger(bot))
