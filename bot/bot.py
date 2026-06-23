import discord

import config
import db
from parser import parse_maptap_message

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
conn = db.connect(config.DATABASE_URL)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}. Watching channels: {list(config.CHANNEL_CHAT_MAP.values())}")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    chat = config.CHANNEL_CHAT_MAP.get(message.channel.id)
    if chat is None:
        return

    parsed = parse_maptap_message(message.content, year=message.created_at.year)
    if parsed is None:
        return

    player = message.author.display_name
    inserted = db.insert_score(
        conn,
        message_id=message.id,
        chat=chat,
        player=player,
        date_str=parsed["date"],
        rounds=parsed["rounds"],
        total=parsed["total"],
    )
    if inserted:
        await message.add_reaction("✅")
        print(f"[{chat}] {player} {parsed['date']}: {parsed['rounds']} -> {parsed['total']}")


client.run(config.DISCORD_TOKEN)
