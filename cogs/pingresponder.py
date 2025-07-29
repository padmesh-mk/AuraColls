import discord
from discord.ext import commands
import json

class BotPingResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_prefixes(self, guild_id):
        try:
            with open("prefixes.json", "r") as f:
                data = json.load(f)
            prefixes = data.get(str(guild_id), ['a!'])
            return prefixes if isinstance(prefixes, list) else [prefixes]
        except (FileNotFoundError, json.JSONDecodeError):
            return ['a!']

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Respond only if the message is just the bot mention
        if message.content.strip() == self.bot.user.mention:
            prefixes = self.get_prefixes(message.guild.id)
            prefix_str = ', '.join(f'`{p}`' for p in prefixes)

            embed = discord.Embed(
                title="Yes? I’m here!",
                description=(
                    f"➤ **My prefixes in this server are:**\n"
                    f"> {prefix_str}\n\n"
                    f"➤ **[Join the support server](https://discord.gg/becvfQ9fCr)**"
                ),
                color=0xFF6B6B
            )
            embed.set_footer(text="Type ahelp command to learn more.")
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotPingResponder(bot))
