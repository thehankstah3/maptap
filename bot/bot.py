import json
import os

import discord

import config
import db
from parser import (
    parse_maptap_message,
    parse_wordle_message,
    parse_wend_message,
    parse_zip_message,
    parse_patches_message,
    parse_tango_message,
    parse_queens_message,
)

# Games with a uniform parser signature: fn(content) -> {"score": int, ...} or None
SIMPLE_GAMES = [
    ("wend", parse_wend_message),
    ("zip", parse_zip_message),
    ("patches", parse_patches_message),
    ("tango", parse_tango_message),
    ("queens", parse_queens_message),
]

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

# JSON object mapping Discord channel ID -> chat name, e.g.:
# {"123456789012345678": "maptap", "234567890123456789": "hcm"}
CHANNEL_CHAT_MAP = {
    int(channel_id): chat
    for channel_id, chat in json.loads(os.environ["CHANNEL_CHAT_MAP"]).items()
}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
conn = db.connect(config.DATABASE_URL)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}. Watching channels: {list(CHANNEL_CHAT_MAP.values())}")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    chat = CHANNEL_CHAT_MAP.get(message.channel.id)
    if chat is None:
        return

    player = message.author.display_name

    maptap = parse_maptap_message(message.content, year=message.created_at.year)
    if maptap is not None:
        inserted = db.insert_result(
            conn,
            message_id=message.id,
            game="maptap",
            chat=chat,
            player=player,
            date_str=maptap["date"],
            data={"rounds": maptap["rounds"]},
            score=maptap["total"],
        )
        if inserted:
            await message.add_reaction("✅")
            print(f"[{chat}] maptap {player} {maptap['date']}: {maptap['rounds']} -> {maptap['total']}")
        return

    wordle = parse_wordle_message(message.content)
    if wordle is not None:
        date_str = message.created_at.date().isoformat()
        inserted = db.insert_result(
            conn,
            message_id=message.id,
            game="wordle",
            chat=chat,
            player=player,
            date_str=date_str,
            data=wordle,
            score=wordle["attempts"],
        )
        if inserted:
            await message.add_reaction("✅")
            print(f"[{chat}] wordle {player} {date_str}: {wordle['attempts']}/6")
        return

    for game, parse_fn in SIMPLE_GAMES:
        parsed = parse_fn(message.content)
        if parsed is None:
            continue
        date_str = message.created_at.date().isoformat()
        inserted = db.insert_result(
            conn,
            message_id=message.id,
            game=game,
            chat=chat,
            player=player,
            date_str=date_str,
            data=parsed,
            score=parsed["score"],
        )
        if inserted:
            await message.add_reaction("✅")
            print(f"[{chat}] {game} {player} {date_str}: {parsed['score']}s")
        return


client.run(DISCORD_TOKEN)
