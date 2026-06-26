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
    player = request.args.get("player")
    with get_conn().cursor() as cur:
        if player:
            cur.execute("SELECT DISTINCT chat FROM results WHERE player = %s ORDER BY chat", (player,))
        else:
            cur.execute("SELECT DISTINCT chat FROM results ORDER BY chat")
        rows = cur.fetchall()
    return jsonify([r[0] for r in rows])


@app.get("/api/games/<chat>")
def list_games(chat):
    with get_conn().cursor() as cur:
        cur.execute("SELECT DISTINCT game FROM results WHERE chat = %s ORDER BY game", (chat,))
        rows = cur.fetchall()
    return jsonify([r[0] for r in rows])


@app.get("/api/results/<chat>/<game>")
def get_results(chat, game):
    with get_conn().cursor() as cur:
        cur.execute(
            "SELECT date, player, data, score FROM results WHERE chat = %s AND game = %s ORDER BY date",
            (chat, game),
        )
        rows = cur.fetchall()
    if not rows:
        abort(404)

    players = sorted({player for _, player, _, _ in rows})
    results = [
        {"date": date, "player": player, "data": json.loads(data), "score": score}
        for date, player, data, score in rows
    ]
    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(
        {"chat": chat, "game": game, "exported_at": exported_at, "players": players, "results": results}
    )


@app.post("/api/results")
def post_result():
    if request.headers.get("X-API-Key") != API_KEY:
        abort(401)

    data = request.get_json(silent=True) or {}
    required = {"game", "chat", "player", "date", "data", "score"}
    if not required.issubset(data):
        abort(400, "Missing required fields: " + ", ".join(sorted(required - data.keys())))

    message_id = f"{data['game']}:{data['chat']}:{data['date']}:{data['player']}"
    inserted = db.insert_result(
        get_conn(),
        message_id=message_id,
        game=data["game"],
        chat=data["chat"],
        player=data["player"],
        date_str=data["date"],
        data=data["data"],
        score=data["score"],
    )
    return jsonify({"inserted": inserted}), 201


# Backward-compatible shim for the existing maptap-only dashboard/extension
# while they're being updated to the generalized /api/results endpoints.
@app.get("/api/scores/<chat>")
def get_scores_legacy(chat):
    with get_conn().cursor() as cur:
        cur.execute(
            "SELECT date, player, data, score FROM results WHERE chat = %s AND game = 'maptap' ORDER BY date",
            (chat,),
        )
        rows = cur.fetchall()
    if not rows:
        abort(404)

    players = sorted({player for _, player, _, _ in rows})
    scores = [
        {"date": date, "player": player, "rounds": json.loads(data)["rounds"], "total": score}
        for date, player, data, score in rows
    ]
    exported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"chat": chat, "exported_at": exported_at, "players": players, "scores": scores})


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=debug)
