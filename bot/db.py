import json

import psycopg2

SCHEMA = """
CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    chat TEXT NOT NULL,
    player TEXT NOT NULL,
    date TEXT NOT NULL,
    rounds TEXT NOT NULL,
    total INTEGER NOT NULL
);
"""


def connect(database_url):
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
    return conn


def insert_score(conn, message_id, chat, player, date_str, rounds, total):
    """Insert a parsed score. Returns False if message_id was already recorded."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scores (message_id, chat, player, date, rounds, total)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING
            """,
            (str(message_id), chat, player, date_str, json.dumps(rounds), total),
        )
        inserted = cur.rowcount > 0
    conn.commit()
    return inserted
