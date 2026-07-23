#!/usr/bin/env python3
"""
Color Palette Generator — enter a hex seed color and instantly get a
5-step complementary palette with hex, RGB, and CSS variables output.
Pure Flask + vanilla JS, zero extra dependencies.
"""

from flask import Flask, jsonify, render_template_string, request
import os
import socket
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Color Palette Generator</title>
    <meta charset="utf-8">
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:Arial,sans-serif;background:#f5f5f5;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
        .card{background:#fff;border-radius:16px;padding:36px;width:100%;max-width:680px;box-shadow:0 8px 24px rgba(0,0,0,.12)}
        h1{font-size:1.6rem;color:#1f2328;margin-bottom:4px}
        .sub{color:#57606a;font-size:.9rem;margin-bottom:26px}
        .row{display:flex;gap:12px;align-items:center;margin-bottom:24px}
        input[type=color]{width:52px;height:44px;border:none;padding:2px;border-radius:8px;cursor:pointer;background:none}
        input[type=text]{flex:1;padding:10px 14px;border:1px solid #d1d5db;border-radius:8px;font-size:1rem;font-family:monospace}
        button{padding:10px 22px;background:#2457d6;color:#fff;border:none;border-radius:8px;font-size:.95rem;cursor:pointer}
        button:hover{background:#1a3fa8}
        .swatches{display:flex;gap:0;border-radius:12px;overflow:hidden;margin-bottom:20px;height:90px}
        .swatch{flex:1;cursor:pointer;position:relative;transition:flex .2s}
        .swatch:hover{flex:2}
        .swatch-label{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);font-size:.7rem;background:rgba(0,0,0,.45);color:#fff;padding:2px 6px;border-radius:4px;white-space:nowrap;opacity:0;transition:opacity .2s}
        .swatch:hover .swatch-label{opacity:1}
        .css-block{background:#1c2a3a;color:#c9d1d9;border-radius:10px;padding:16px 18px;font-family:monospace;font-size:.82rem;line-height:1.7;white-space:pre;overflow-x:auto;margin-bottom:16px}
        .badge{display:inline-block;background:#1fa971;color:#fff;padding:5px 14px;border-radius:20px;font-size:.82rem}
        .links{margin-top:18px}
        .links a{color:#2457d6;text-decoration:none;margin-right:14px;font-size:.85rem}
        .copied{position:fixed;bottom:24px;right:24px;background:#1c2a3a;color:#fff;padding:8px 18px;border-radius:8px;font-size:.85rem;display:none}
    </style>
</head>
<body>
<div class="card">
    <h1>🎨 Color Palette Generator</h1>
    <p class="sub">Pick a seed color and get a deployable 5-step palette with CSS variables.</p>

    <div class="row">
        <input type="color" id="picker" value="#2457d6">
        <input type="text" id="hexInput" value="#2457d6" maxlength="7" placeholder="#rrggbb">
        <button onclick="generate()">Generate</button>
    </div>

    <div class="swatches" id="swatches"></div>
    <div class="css-block" id="cssOut"></div>

    <span class="badge">Running on {{ hostname }}</span>
    <div class="links">
        <a href="/api/palette?color=2457d6">Palette API</a>
        <a href="/health">Health</a>
    </div>
</div>
<div class="copied" id="copied">Copied!</div>

<script>
const picker = document.getElementById('picker');
const hexInput = document.getElementById('hexInput');

picker.addEventListener('input', ()=>{ hexInput.value = picker.value; generate(); });
hexInput.addEventListener('change', ()=>{ const v=hexInput.value; if(/^#[0-9a-f]{6}$/i.test(v)){picker.value=v;generate();} });

function generate(){
    const hex = hexInput.value.replace('#','');
    fetch('/api/palette?color='+hex)
        .then(r=>r.json())
        .then(d=>{
            const sw = document.getElementById('swatches');
            sw.innerHTML = d.palette.map(p=>
                `<div class="swatch" style="background:${p.hex}" onclick="copyText('${p.hex}')">
                    <span class="swatch-label">${p.hex}</span>
                </div>`
            ).join('');

            const css = d.palette.map((p,i)=>
                `  --color-${i+1}: ${p.hex};  /* rgb(${p.rgb}) */`
            ).join('\n');
            document.getElementById('cssOut').textContent =
                ':root {\n' + css + '\n}';
        });
}

function copyText(t){
    navigator.clipboard.writeText(t).catch(()=>{});
    const el = document.getElementById('copied');
    el.style.display='block';
    setTimeout(()=>el.style.display='none', 1500);
}

generate();
</script>
</body>
</html>
"""

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))

def build_palette(r: int, g: int, b: int) -> list[dict]:
    """Return a 5-step palette: darker → base → lighter (split-complementary shades)."""
    steps = [0.35, 0.65, 1.0, 1.35, 1.65]
    palette = []
    for s in steps:
        nr, ng, nb = clamp(r * s), clamp(g * s), clamp(b * s)
        hex_val = rgb_to_hex(nr, ng, nb)
        palette.append({"hex": hex_val, "rgb": f"{nr},{ng},{nb}"})
    return palette

@app.route("/")
def home():
    return render_template_string(HTML, hostname=socket.gethostname())

@app.route("/api/palette")
def palette():
    color = request.args.get("color", "2457d6").lstrip("#")
    if len(color) != 6:
        return jsonify({"error": "invalid color"}), 400
    try:
        r, g, b = hex_to_rgb(color)
    except ValueError:
        return jsonify({"error": "invalid hex"}), 400
    pal = build_palette(r, g, b)
    return jsonify({
        "seed": f"#{color}",
        "palette": pal,
        "generated_at": datetime.now().isoformat(),
        "host": socket.gethostname(),
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5003)))
