"""One-time migration: copy the old single-game `scores` table into the new
game-agnostic `results` table (game='maptap' for every existing row).
The old `scores` table is left untouched so this is safe to re-run or roll back from.
"""
import json

import db
from config import DATABASE_URL


def migrate():
    conn = db.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute("SELECT message_id, chat, player, date, rounds, total FROM scores")
        rows = cur.fetchall()

    inserted = 0
    for message_id, chat, player, date_str, rounds, total in rows:
        data = {"rounds": json.loads(rounds)}
        if db.insert_result(conn, message_id, "maptap", chat, player, date_str, data, total):
            inserted += 1
    print(f"Inserted {inserted} of {len(rows)} rows from scores into results")


if __name__ == "__main__":
    migrate()
