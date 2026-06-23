import json
import sys

import db
from config import DATABASE_URL


def migrate(json_path):
    with open(json_path) as f:
        data = json.load(f)

    chat = data["chat"]
    conn = db.connect(DATABASE_URL)
    inserted = 0
    for row in data["scores"]:
        message_id = f"json-import:{chat}:{row['date']}:{row['player']}"
        if db.insert_score(
            conn,
            message_id=message_id,
            chat=chat,
            player=row["player"],
            date_str=row["date"],
            rounds=row["rounds"],
            total=row["total"],
        ):
            inserted += 1
    print(f"Inserted {inserted} of {len(data['scores'])} rows from {json_path} (chat={chat})")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_json.py <path-to-data_X.json>")
        sys.exit(1)
    migrate(sys.argv[1])
