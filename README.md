# Amazon Price Tracking Discord Bot

Discord bot that tracks Amazon prices and sends notifications when price changes occur.

---

## Features

- Track Amazon products via URL
- Price history per user
- Detection of price increases and decreases
- Private Discord messages on price changes
- Multi-user support

---

## Requirements

- Python 3.10+
- Internet connection
- Discord bot token

---

## Installation

### 1. Clone the project

<pre>
git clone https://github.com/your-username/amazon-price-tracker-bot.git
cd amazon-price-tracker-bot
</pre>

### 2. Install dependencies

<pre>
pip install -r requirements.txt
</pre>

---

## Configuration (.env required)

Create a `.env` file at the root of the project (same folder as `main.py`):

DISCORD_TOKEN=your_token_here

---

## Create a Discord bot + get token

https://discord.com/developers/applications  

Steps:

- Create a “New Application”
- Go to the Bot tab
- Click “Add Bot”
- Copy the TOKEN
- Paste it into the `.env` file

---

## Run the bot

<pre>
python main.py
</pre>
