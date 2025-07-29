import discord
from discord.ext import commands
import json
import os

PREFIX_FILE = 'prefixes.json'
DEFAULT_PREFIX = 'a'

def ensure_prefix_file():
    if not os.path.exists(PREFIX_FILE):
        with open(PREFIX_FILE, 'w') as f:
            json.dump({}, f)

def get_prefix_list(guild_id):
    with open(PREFIX_FILE, 'r') as f:
        data = json.load(f)
    return data.get(str(guild_id), [DEFAULT_PREFIX])

def save_prefix_list(guild_id, prefixes):
    with open(PREFIX_FILE, 'r') as f:
        data = json.load(f)
    data[str(guild_id)] = prefixes
    with open(PREFIX_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class Prefix(commands.Cog):
    """Manage the custom command prefixes for each server."""
    
    def __init__(self, bot):
        self.bot = bot
        ensure_prefix_file()

    @commands.hybrid_group(name="prefix", with_app_command=True, invoke_without_command=True)
    async def prefix(self, ctx):
        await ctx.send("Use `prefix list`, `prefix add`, or `prefix remove`.")

    @prefix.command(name="list", description="Show the current prefixes")
    async def prefix_list(self, ctx):
        prefixes = get_prefix_list(ctx.guild.id)
        formatted = "\n".join(f"`{p}` {'(default)' if p == DEFAULT_PREFIX else ''}" for p in prefixes)
        embed = discord.Embed(
            title="<:ap_support:1382716862256910437> Current Prefixes",
            description=formatted,
            color=0xFF6B6B
        )
        await ctx.send(embed=embed)

    @prefix.command(name="add", description="Add a new prefix")
    @commands.has_permissions(administrator=True)
    async def prefix_add(self, ctx, new_prefix: str):
        prefixes = get_prefix_list(ctx.guild.id)
        if new_prefix in prefixes:
            return await ctx.send("<:ap_crossmark:1382760353904988230> This prefix already exists.")
        prefixes.append(new_prefix)
        save_prefix_list(ctx.guild.id, prefixes)
        await ctx.send(f"<:ap_checkmark:1382760062728273920> Added prefix `{new_prefix}`.")

    @prefix.command(name="remove", description="Remove an existing prefix")
    @commands.has_permissions(administrator=True)
    async def prefix_remove(self, ctx, old_prefix: str):
        prefixes = get_prefix_list(ctx.guild.id)
        if old_prefix == DEFAULT_PREFIX:
            return await ctx.send("<:ap_crossmark:1382760353904988230> You can't remove the default prefix.")
        if old_prefix not in prefixes:
            return await ctx.send("<:ap_crossmark:1382760353904988230> That prefix doesn't exist.")
        prefixes.remove(old_prefix)
        save_prefix_list(ctx.guild.id, prefixes)
        await ctx.send(f"🗑️ Removed prefix `{old_prefix}`.")

async def setup(bot):
    await bot.add_cog(Prefix(bot))
