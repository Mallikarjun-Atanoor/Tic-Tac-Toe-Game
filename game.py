import os
import sqlite3
import json
from flask import Flask, render_template, request, redirect

DB = os.environ.get("DB_PATH", "score.db")
app = Flask(__name__)
DB = "score.db"


# create tables
conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    player1 TEXT,
    player2 TEXT,
    board TEXT,
    current_player TEXT,
    winner TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS scores (
    name TEXT PRIMARY KEY,
    wins INTEGER
)
""")

conn.commit()
conn.close()


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/start", methods=["POST"])
def start():
    p1 = request.form["player1"]
    p2 = request.form["player2"]

    board = [""] * 9

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM games")
    c.execute("INSERT INTO games (player1, player2, board, current_player, winner) VALUES (?,?,?,?,?)",
              (p1, p2, json.dumps(board), "X", ""))
    conn.commit()
    conn.close()

    return redirect("/game")


@app.route("/game")
def game():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT player1, player2, board, current_player, winner FROM games LIMIT 1")
    row = c.fetchone()
    conn.close()

    if not row:
        return redirect("/")

    board = json.loads(row[2])

    # fetch scoreboard
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM scores")
    scores = c.fetchall()
    conn.close()

    return render_template("game.html",
                           player1=row[0],
                           player2=row[1],
                           board=board,
                           current=row[3],
                           winner=row[4],
                           scores=scores)


@app.route("/move", methods=["POST"])
def move():
    pos = int(request.form["position"])

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT player1, player2, board, current_player, winner FROM games LIMIT 1")
    row = c.fetchone()

    p1, p2 = row[0], row[1]
    board = json.loads(row[2])
    current = row[3]
    winner = row[4]

    if winner:
        conn.close()
        return redirect("/game")

    if board[pos] == "":
        board[pos] = current

    # winner check
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for w in wins:
        if board[w[0]] == board[w[1]] == board[w[2]] != "":
            winner = board[w[0]]

    # update score
    if winner:
        winner_name = p1 if winner == "X" else p2
        c.execute("SELECT wins FROM scores WHERE name=?", (winner_name,))
        r = c.fetchone()
        if r:
            c.execute("UPDATE scores SET wins=? WHERE name=?",
                      (r[0] + 1, winner_name))
        else:
            c.execute("INSERT INTO scores VALUES (?,?)",
                      (winner_name, 1))

    next_player = "O" if current == "X" else "X"

    c.execute("UPDATE games SET board=?, current_player=?, winner=?",
              (json.dumps(board), next_player, winner))
    conn.commit()
    conn.close()

    return redirect("/game")


@app.route("/reset")
def reset():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM games")
    conn.commit()
    conn.close()
    return redirect("/")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)