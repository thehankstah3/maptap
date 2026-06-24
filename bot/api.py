import json
import os
from datetime import datetime

from flask import Flask, jsonify, abort, g, request
from flask_cors import CORS

import db
from config import DATABASE_URL

API_KEY = os.environ["API_KEY"]

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


@app.post("/api/scores")
def post_score():
    if request.headers.get("X-API-Key") != API_KEY:
        abort(401)

    data = request.get_json(silent=True) or {}
    required = {"chat", "player", "date", "rounds", "total"}
    if not required.issubset(data):
        abort(400, "Missing required fields: " + ", ".join(sorted(required - data.keys())))

    message_id = f"ext:{data['chat']}:{data['date']}:{data['player']}"
    inserted = db.insert_score(
        get_conn(),
        message_id=message_id,
        chat=data["chat"],
        player=data["player"],
        date_str=data["date"],
        rounds=data["rounds"],
        total=data["total"],
    )
    return jsonify({"inserted": inserted}), 201


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=debug)
