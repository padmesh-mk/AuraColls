import discord
from discord.ext import commands
import os
import asyncio
import datetime
import logging
import json
from dotenv import load_dotenv
from console_logger import DiscordLogHandler
from vote_remind import start_reminder_loop

# Load environment variables
load_dotenv()

# Get values from .env
TOKEN = os.getenv("DISCORD_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_LOG_WEBHOOK")
RESTART_CHANNEL_ID = int(os.getenv("BOT_RESTART_CHANNEL_ID", 0))
GUILD_ID = int(os.getenv("MAIN_GUILD_ID", 0))

# Prefix config
PREFIX_FILE = 'prefixes.json'
DEFAULT_PREFIX = 'a'

if not os.path.exists(PREFIX_FILE):
    with open(PREFIX_FILE, 'w') as f:
        json.dump({}, f)

def get_prefix(bot, message):
    if not message.guild:
        return [DEFAULT_PREFIX, DEFAULT_PREFIX + ' ']
    try:
        with open(PREFIX_FILE, 'r') as f:
            data = json.load(f)
        guild_prefix = data.get(str(message.guild.id), DEFAULT_PREFIX)
        if isinstance(guild_prefix, str):
            return [guild_prefix, guild_prefix + ' ']
        # If it's a list
        return guild_prefix + [p + ' ' for p in guild_prefix]
    except:
        return [DEFAULT_PREFIX, DEFAULT_PREFIX + ' ']


# Intents and bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.start_time = datetime.datetime.now(datetime.UTC)

# -------------------- DISCORD BOT EVENTS --------------------

async def send_restart_message():
    await bot.wait_until_ready()
    await asyncio.sleep(2)
    if not RESTART_CHANNEL_ID:
        return
    channel = bot.get_channel(RESTART_CHANNEL_ID)
    if channel:
        try:
            await channel.send("<a:ap_uptime:1382717912120430702> **AuraColls** is back online!")
        except:
            pass

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash commands')
    except Exception as e:
        print(f'❌ Slash command sync error: {e}')
    await send_restart_message()

# -------------------- DYNAMIC COG LOADER --------------------

async def load_cogs():
    base_path = "cogs"
    for file in os.listdir(base_path):
        if file.endswith(".py"):
            module = f"{base_path}.{file[:-3]}"
            try:
                await bot.load_extension(module)
                logging.info(f"✅ Loaded cog: {module}")
            except Exception as e:
                logging.error(f"❌ Failed to load cog {module}: {e}")

                
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Silently ignore unknown commands
    raise error  # Raise others so they're logged or handled elsewhere
    
# -------------------- MAIN ENTRY --------------------

async def main():
    handler = DiscordLogHandler(webhook_url=WEBHOOK_URL)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)
    await handler.start()
    logging.info("🦵 Discord bot logging has started.")

    async with bot:
        await load_cogs()
        bot.loop.create_task(start_reminder_loop(bot))  
        logging.info("🚀 Bot starting now...")
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
