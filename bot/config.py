import json
import os

from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DATABASE_URL = os.environ["DATABASE_URL"]

# JSON object mapping Discord channel ID -> chat name, e.g.:
# {"123456789012345678": "maptap", "234567890123456789": "hcm"}
CHANNEL_CHAT_MAP = {
    int(channel_id): chat
    for channel_id, chat in json.loads(os.environ["CHANNEL_CHAT_MAP"]).items()
}
