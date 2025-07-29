# 🎁 AuraColls - Discord Collectibles Bot

AuraColls is a dynamic, collectible-focused Discord bot made with Python. It allows users to earn, trade, and grow their collection of virtual items using a duplication-based economy — with daily rewards, user stats, leaderboards, and more!

> 👨‍💻 Developed by [@PadmeshMK](https://github.com/padmesh-mk)

---

## 🌟 Key Features

- 🧸 Send & Collect unique collectibles like heart, teddy, music, etc...
- 🔁 Duplication-style trades (send 1 → receive 2!)
- 📦 View collectibles with advanced filtering & pagination
- 🗓️ Claim daily rewards (points, streaks, random collectible)
- 🎯 Track your sending activity with the points leaderboard
- 🔐 Owner-only and tradable collectible types
- 🧠 Slash + Prefix command support
- 💾 JSON-based lightweight storage

---

## 🧾 Collectible Commands

### 📦 View & Manage
| Command | Description |
|---------|-------------|
| `list` / `/list` | View your collection with filters & pages. |

### 🎁 Daily Reward
| Command | Description |
|---------|-------------|
| `daily` / `/daily` | Claim random collectibles & points daily. |

### 💞 Send Collectibles
| Command | Description |
|---------|-------------|
| `aheart`, `ateddy`, etc. | Send a collectible to a user. Limited by cooldowns. |

### 🏆 Leaderboard
| Command | Description |
|---------|-------------|
| `pointslb` / `/pointslb` | Show top users ranked by total points earned. |

### 📈 Voting
| Command | Description |
|---------|-------------|
| `vote` / `/vote` | Vote for bot to earn a custom voter collectible. |

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AuraColls.git
cd AuraColls
````

### 2. Create `config.json` for bot token

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN"
}
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the bot

```bash
python main.py
```

---

## 📁 Project Structure

```
AuraColls/
├── main.py                  # Bot launcher
├── .env                     # Bot token (excluded in .gitignore)
├── requirements.txt         # Dependencies
├── version.json             # Bot version + changelog
├── collectibles.json        # Main collectible inventory
├── points.json              # Points per user
├── daily.json               # Daily claim tracking
├── tradablecoll.json        # Tradable collectibles list
├── restrictedcoll.json      # Owner-only collectibles
├── collectible_info.json    # Emoji + metadata
└── cogs/
    ├── view_collectibles.py
    ├── send_collectibles.py
    ├── daily.py
    ├── points.py
    ├── version.py
    └── coll_display.py
```

---

## 📦 JSON Data Format

Your collectibles, cooldowns, daily streaks, and points are all stored using editable JSON files. This makes backup and customization easy — no external database required!

---

## 👤 Owner Commands

Certain commands (e.g. modifying user data, force-adding collectibles) are locked to a specific user ID for bot maintenance and control. Edit the ID in the source files.

---

## 📜 License

This project is licensed under the **MIT License** — free for personal use.

---

## 🙌 Credits

Made with ❤️ by [Padmesh](https://github.com/padmesh-mk)

Join the support server if you have questions or need help!
