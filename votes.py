import json
import time
import os

VOTES_FILE = "votes.json"

def load_votes():
    if not os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "w") as f:
            json.dump({}, f)
    with open(VOTES_FILE, "r") as f:
        return json.load(f)

def save_votes(data):
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_data(user_id):
    data = load_votes()
    user = data.get(user_id, {})
    if not user:
        user = {
            "votes": 0,
            "last_vote": 0,
            "rank": "N/A"
        }
    else:
        user["rank"] = get_user_rank(user_id)
        if "last_vote" not in user:
            user["last_vote"] = 0
    return user

def update_user_vote(user_id):
    data = load_votes()
    now = int(time.time())  # ✅ save as UNIX timestamp
    if user_id in data:
        data[user_id]["votes"] += 1
        data[user_id]["last_vote"] = now
    else:
        data[user_id] = {
            "votes": 1,
            "last_vote": now
        }
    save_votes(data)

def get_user_rank(user_id):
    data = load_votes()
    sorted_users = sorted(data.items(), key=lambda x: x[1]["votes"], reverse=True)
    for index, (uid, _) in enumerate(sorted_users, start=1):
        if uid == user_id:
            return index
    return "N/A"

def get_leaderboard(top_n=None):
    data = load_votes()
    lb = []
    for user_id, info in data.items():
        lb.append((user_id, {
            "votes": info.get("votes", 0)
        }))
    lb_sorted = sorted(lb, key=lambda x: x[1]["votes"], reverse=True)
    return lb_sorted[:top_n] if top_n else lb_sorted
