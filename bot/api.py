import json
import os
from datetime import datetime

from flask import Flask, jsonify, abort, g
from flask_cors import CORS

import db
from config import DATABASE_URL

app = Flask(__name__)
CORS(app)


def get_conn():
    if "conn" not in g:
        g.conn = db.connect(DATABASE_URL)
    return g.conn


@app.teardown_appcontext
def close_conn(exception=None):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()


@app.get("/api/chats")
def list_chats():
    with get_conn().cursor() as cur:
        cur.execute("SELECT DISTINCT chat FROM scores ORDER BY chat")
        rows = cur.fetchall()
    return jsonify([r[0] for r in rows])


@app.get("/api/scores/<chat>")
def get_scores(chat):
    with get_conn().cursor() as cur:
        cur.execute(
            "SELECT date, player, rounds, total FROM scores WHERE chat = %s ORDER BY date",
            (chat,),
        )
        rows = cur.fetchall()
    if not rows:
        abort(404)

    players = sorted({player for _, player, _, _ in rows})
    scores = [
        {"date": date, "player": player, "rounds": json.loads(rounds), "total": total}
        for date, player, rounds, total in rows
    ]
    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"chat": chat, "exported_at": exported_at, "players": players, "scores": scores})


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=debug)
