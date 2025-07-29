# vote_remind.py
import json
import os
import datetime
import asyncio
import discord  # Make sure you have this import

REMIND_FILE = "vote_remind.json"

def load_reminders():
    if not os.path.exists(REMIND_FILE):
        with open(REMIND_FILE, "w") as f:
            json.dump({}, f)
    with open(REMIND_FILE, "r") as f:
        return json.load(f)

def save_reminders(data):
    with open(REMIND_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_to_reminder(user_id):
    data = load_reminders()
    # Store as Unix timestamp (int)
    next_vote = int((datetime.datetime.utcnow() + datetime.timedelta(hours=12)).timestamp())
    data[user_id] = next_vote
    save_reminders(data)

def is_on_cooldown(user_id):
    data = load_reminders()
    if user_id not in data:
        return False

    reminder = data[user_id]
    # Parse both string and int formats
    try:
        if isinstance(reminder, int):
            next_time = datetime.datetime.utcfromtimestamp(reminder)
        else:
            next_time = datetime.datetime.strptime(reminder, "%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return False

    return datetime.datetime.utcnow() < next_time

async def start_reminder_loop(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        data = load_reminders()
        now = datetime.datetime.utcnow()
        to_remove = []

        for user_id, reminder in data.items():
            try:
                # Handle both string and int formats
                if isinstance(reminder, int):
                    remind_time = datetime.datetime.utcfromtimestamp(reminder)
                else:
                    remind_time = datetime.datetime.strptime(reminder, "%Y-%m-%d %H:%M:%S UTC")

                if now >= remind_time:
                    user = bot.get_user(int(user_id))
                    if user:
                        try:
                            await user.send("<:ap_vote:1395506333834543144> Hey! It's time to vote for AuraColl again!\nVote using `avote` or `/vote`.")
                        except discord.Forbidden:
                            pass  # Can't DM user
                    to_remove.append(user_id)

            except Exception as e:
                print(f"Error handling reminder for {user_id}: {e}")

        for user_id in to_remove:
            del data[user_id]

        save_reminders(data)
        await asyncio.sleep(60)  # Check every minute
