#!/usr/bin/env python3
"""
Live Vote — audience polling app.
Cast a vote for your favourite IBM Cloud product and watch the tally update live.
No database required — votes are kept in memory (resets on restart).
"""

from flask import Flask, jsonify, render_template_string, request
import os
import socket
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

CHOICES = ["watsonx.ai", "Red Hat OpenShift", "IBM Cloud Pak", "DataStage", "Instana"]
votes: dict[str, int] = defaultdict(int)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Poll</title>
    <meta charset="utf-8">
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:Arial,sans-serif;background:#0f1923;color:#e8ecf0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
        .card{background:#1c2a3a;border-radius:16px;padding:40px;width:100%;max-width:620px;box-shadow:0 12px 40px rgba(0,0,0,.5)}
        h1{color:#4fa3ff;font-size:1.7rem;margin-bottom:4px}
        .sub{color:#8a9ab0;font-size:.9rem;margin-bottom:28px}
        .choice{display:flex;align-items:center;gap:12px;margin-bottom:14px}
        .choice button{
            flex:0 0 180px;background:#2457d6;color:#fff;border:none;padding:10px 16px;
            border-radius:8px;font-size:.95rem;cursor:pointer;text-align:left;transition:background .15s
        }
        .choice button:hover{background:#3a6ef0}
        .bar-wrap{flex:1;background:#0f1923;border-radius:6px;height:28px;overflow:hidden}
        .bar{height:100%;background:linear-gradient(90deg,#2457d6,#4fa3ff);border-radius:6px;transition:width .4s ease;min-width:0}
        .count{flex:0 0 40px;text-align:right;color:#8a9ab0;font-size:.9rem}
        .total{margin-top:20px;color:#8a9ab0;font-size:.85rem}
        .badge{display:inline-block;margin-top:20px;background:#1fa971;color:#fff;padding:6px 14px;border-radius:20px;font-size:.85rem}
        .links{margin-top:22px}
        .links a{color:#4fa3ff;text-decoration:none;margin-right:16px;font-size:.85rem}
        .voted{border:2px solid #1fa971!important;background:#14532d!important}
    </style>
</head>
<body>
<div class="card">
    <h1>📊 Live Poll</h1>
    <p class="sub">Vote for your favourite IBM technology — results update instantly.</p>

    <div id="choices"></div>
    <p class="total">Total votes: <strong id="total">0</strong></p>
    <p class="sub" id="ts"></p>
    <span class="badge">Running on {{ hostname }}</span>
    <div class="links">
        <a href="/results">Results API</a>
        <a href="/reset">Reset Votes</a>
        <a href="/health">Health</a>
    </div>
</div>

<script>
const CHOICES = {{ choices|tojson }};
let myVote = null;

function render(data){
    const max = Math.max(...Object.values(data.votes), 1);
    const total = Object.values(data.votes).reduce((a,b)=>a+b,0);
    document.getElementById('total').textContent = total;
    document.getElementById('ts').textContent = 'Last updated: ' + data.timestamp;
    const wrap = document.getElementById('choices');
    wrap.innerHTML = '';
    CHOICES.forEach(c => {
        const v = data.votes[c] || 0;
        const pct = Math.round(v / max * 100);
        const isVoted = myVote === c;
        wrap.innerHTML += `
        <div class="choice">
            <button class="${isVoted?'voted':''}" onclick="vote('${c}')">${c}</button>
            <div class="bar-wrap"><div class="bar" style="width:${pct}%"></div></div>
            <span class="count">${v}</span>
        </div>`;
    });
}

function vote(choice){
    myVote = choice;
    fetch('/vote', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({choice})})
        .then(r=>r.json()).then(render);
}

function poll(){
    fetch('/results').then(r=>r.json()).then(render);
}

poll();
setInterval(poll, 3000);
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        HTML,
        hostname=socket.gethostname(),
        choices=CHOICES,
    )

@app.route("/vote", methods=["POST"])
def cast_vote():
    data = request.get_json(force=True)
    choice = data.get("choice", "")
    if choice in CHOICES:
        votes[choice] += 1
    return _results_payload()

@app.route("/results")
def results():
    return jsonify(_results_payload())

@app.route("/reset")
def reset():
    votes.clear()
    return jsonify({"status": "reset", "timestamp": datetime.now().isoformat()})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

def _results_payload():
    return {
        "votes": {c: votes[c] for c in CHOICES},
        "total": sum(votes.values()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)))
