import json

import psycopg2

SCHEMA = """
CREATE TABLE IF NOT EXISTS results (
    id SERIAL PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,
    game TEXT NOT NULL,
    chat TEXT NOT NULL,
    player TEXT NOT NULL,
    date TEXT NOT NULL,
    data TEXT NOT NULL,
    score INTEGER NOT NULL
);
"""


def connect(database_url):
    conn = psycopg2.connect(database_url)
    with conn.cursor() as cur:
        cur.execute(SCHEMA)
    conn.commit()
    return conn


def insert_result(conn, message_id, game, chat, player, date_str, data, score):
    """Insert a parsed game result. Returns False if message_id was already recorded."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO results (message_id, game, chat, player, date, data, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO NOTHING
            """,
            (str(message_id), game, chat, player, date_str, json.dumps(data), score),
        )
        inserted = cur.rowcount > 0
    conn.commit()
    return inserted
