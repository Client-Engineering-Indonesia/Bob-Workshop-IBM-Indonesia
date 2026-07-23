#!/usr/bin/env python3
"""
Request Inspector — echo every HTTP request back to the browser in a clean UI.
Useful for demoing that deployed routes, headers, and env vars are wired correctly.
Keeps a rolling log of the last 20 requests in memory.
"""

from flask import Flask, jsonify, render_template_string, request
import os
import socket
import json
from datetime import datetime
from collections import deque

app = Flask(__name__)

LOG: deque = deque(maxlen=20)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Request Inspector</title>
    <meta charset="utf-8">
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:Arial,sans-serif;background:#0d1117;color:#c9d1d9;min-height:100vh;padding:32px 24px}
        .page{max-width:780px;margin:auto}
        h1{color:#58a6ff;font-size:1.6rem;margin-bottom:4px}
        .sub{color:#8b949e;font-size:.88rem;margin-bottom:24px}
        .send-row{display:flex;gap:10px;margin-bottom:28px;flex-wrap:wrap}
        .send-row select,.send-row input{padding:9px 12px;background:#161b22;border:1px solid #30363d;color:#c9d1d9;border-radius:8px;font-size:.9rem}
        .send-row select{width:110px}
        .send-row input{flex:1;min-width:160px}
        .send-row button{padding:9px 20px;background:#238636;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:.9rem}
        .send-row button:hover{background:#2ea043}
        .entry{background:#161b22;border:1px solid #30363d;border-radius:10px;margin-bottom:14px;overflow:hidden}
        .entry-head{display:flex;align-items:center;gap:10px;padding:10px 14px;background:#1c2128;cursor:pointer}
        .method{font-weight:bold;font-size:.8rem;padding:3px 8px;border-radius:5px;min-width:52px;text-align:center}
        .GET{background:#1f4d8a;color:#79c0ff}
        .POST{background:#3b2f00;color:#ffa657}
        .PUT{background:#1f3b1f;color:#56d364}
        .DELETE{background:#3b1f1f;color:#ff7b72}
        .path{flex:1;font-family:monospace;font-size:.9rem;color:#e6edf3}
        .ts{color:#8b949e;font-size:.78rem}
        .entry-body{padding:14px;display:none;border-top:1px solid #30363d}
        .entry-body.open{display:block}
        .section{margin-bottom:12px}
        .section h4{color:#8b949e;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px}
        pre{background:#0d1117;border-radius:6px;padding:10px 12px;font-size:.8rem;overflow-x:auto;line-height:1.55;color:#c9d1d9}
        .badge{display:inline-block;background:#1fa971;color:#fff;padding:5px 14px;border-radius:20px;font-size:.82rem;margin-bottom:16px}
        .empty{color:#8b949e;font-size:.9rem;padding:20px 0}
        .links a{color:#58a6ff;text-decoration:none;margin-right:14px;font-size:.85rem}
        .counter{float:right;color:#8b949e;font-size:.82rem;margin-top:2px}
    </style>
</head>
<body>
<div class="page">
    <h1>🔍 Request Inspector</h1>
    <p class="sub">Every HTTP request to this app is captured and displayed below. Use the sender to test live.</p>
    <span class="badge">{{ hostname }}</span>
    <span class="counter" id="counter"></span>

    <div class="send-row">
        <select id="method">
            <option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option>
        </select>
        <input type="text" id="pathInput" value="/echo/hello" placeholder="/echo/...">
        <button onclick="sendReq()">Send Request</button>
    </div>

    <div id="log"></div>
    <div class="links"><a href="/api/log">Log API (JSON)</a><a href="/health">Health</a></div>
</div>

<script>
function sendReq(){
    const method = document.getElementById('method').value;
    const path = document.getElementById('pathInput').value || '/echo/test';
    fetch(path, {method}).then(()=>refresh());
}

function refresh(){
    fetch('/api/log').then(r=>r.json()).then(data=>{
        document.getElementById('counter').textContent = data.length + ' request(s)';
        const wrap = document.getElementById('log');
        if(!data.length){ wrap.innerHTML='<p class="empty">No requests yet — send one above!</p>'; return; }
        wrap.innerHTML = data.map((e,i)=>`
            <div class="entry">
                <div class="entry-head" onclick="toggle(${i})">
                    <span class="method ${e.method}">${e.method}</span>
                    <span class="path">${e.path}</span>
                    <span class="ts">${e.timestamp}</span>
                </div>
                <div class="entry-body" id="eb${i}">
                    <div class="section"><h4>Headers</h4><pre>${JSON.stringify(e.headers,null,2)}</pre></div>
                    <div class="section"><h4>Query Params</h4><pre>${JSON.stringify(e.query,null,2)}</pre></div>
                    <div class="section"><h4>Body</h4><pre>${e.body||'(empty)'}</pre></div>
                    <div class="section"><h4>Client</h4><pre>${JSON.stringify(e.client,null,2)}</pre></div>
                </div>
            </div>`).join('');
    });
}

function toggle(i){
    const el = document.getElementById('eb'+i);
    el.classList.toggle('open');
}

refresh();
setInterval(refresh, 4000);
</script>
</body>
</html>
"""

def capture():
    """Capture the current request into the rolling log."""
    entry = {
        "id": len(LOG) + 1,
        "method": request.method,
        "path": request.full_path.rstrip("?"),
        "headers": dict(request.headers),
        "query": dict(request.args),
        "body": request.get_data(as_text=True) or None,
        "client": {
            "ip": request.remote_addr,
            "user_agent": request.user_agent.string,
        },
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    LOG.appendleft(entry)
    return entry

@app.route("/")
def home():
    return render_template_string(HTML, hostname=socket.gethostname())

@app.route("/echo", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/echo/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def echo(path):
    entry = capture()
    return jsonify(entry), 200

@app.route("/api/log")
def api_log():
    return jsonify(list(LOG))

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "host": socket.gethostname()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5004)))
