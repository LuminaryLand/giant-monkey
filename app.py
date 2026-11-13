import streamlit as st

st.set_page_config(
    page_title="Giant Monkey: Jungle Shootout",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: Jungle Shootout")
st.markdown(
    "Shoot projectiles at incoming rival boxer monkeys, eat meat buffets (🥩) to level up, and survive the jungle!"
)

with st.sidebar:
    st.header("🎮 Controls")
    st.markdown("""
    - **Move:** Arrow Keys or `W`, `A`, `S`, `D`
    - **Shoot:** `SPACEBAR`
    - **Objective:** Blast rival monkeys & eat meat!
    """)
    st.divider()
    game_speed = st.slider("Game Difficulty / Speed", 1, 3, 1)

game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ margin: 0; background-color: #111; color: white; font-family: monospace; text-align: center; }}
        .container {{ position: relative; display: inline-block; }}
        canvas {{ background: #5dade2; display: block; margin: 0 auto; border: 4px solid #27ae60; cursor: pointer; image-rendering: pixelated; }}
        #overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; }}
        h2 {{ color: #f1c40f; margin: 0 0 10px 0; }}
        p {{ color: #ddd; font-size: 14px; margin: 0; }}
    </style>
</head>
<body>
    <div class="container" onclick="start()">
        <canvas id="cv" width="700" height="400"></canvas>
        <div id="overlay">
            <h2>▶ CLICK TO START BRAWL</h2>
            <p>Click anywhere to play</p>
        </div>
    </div>
    <script>
        const cv = document.getElementById("cv");
        const ctx = cv.getContext("2d");
        const overlay = document.getElementById("overlay");
        let running = false;
        function start() {{ if(!running) {{ running = true; overlay.style.display = "none"; loop(); }} }}

        let score = 0, level = 1, hp = 100, maxHp = 100, spd = {game_speed};
        let p = {{ x: 80, y: 240, w: 36, h: 36, s: 3.5 }};
        let bullets = [];
        let opponents = [{{ x: 580, y: 240, w: 34, h: 34, s: 0.6 * spd, health: 30, max: 30 }}];
        let meats = [{{ x: 320, y: 260, r: 10 }}];
        let keys = {{}};

        window.addEventListener('keydown', e => {{
            if(!running) return;
            keys[e.code] = true;
            if(e.code === 'Space') {{
                e.preventDefault();
                bullets.push({{ x: p.x + 28, y: p.y, s: 7, r: 5 }});
            }}
        }});
        window.addEventListener('keyup', e => {{ keys[e.code] = false; }});

        function update() {{
            if((keys['ArrowLeft']||keys['KeyA']) && p.x > 20) p.x -= p.s;
            if((keys['ArrowRight']||keys['KeyD']) && p.x < cv.width/2) p.x += p.s;
            if((keys['ArrowUp']||keys['KeyW']) && p.y > 180) p.y -= p.s;
            if((keys['ArrowDown']||keys['KeyS']) && p.y < cv.height - 75) p.y += p.s;

            bullets.forEach((b, i) => {{
                b.x += b.s;
                if(b.x > cv.width) bullets.splice(i, 1);
            }});

            opponents.forEach((op, idx) => {{
                op.x -= op.s;
                if(op.x < -40) {{ op.x = cv.width + 50; op.y = Math.random()*80 + 190; }}

                bullets.forEach((b, bi) => {{
                    if(Math.hypot(b.x - op.x, b.y - op.y) < 24) {{
                        op.health -= 15;
                        bullets.splice(bi, 1);
                        if(op.health <= 0) {{
                            opponents.splice(idx, 1);
                            score += 50;
                            opponents.push({{ x: cv.width + 50, y: Math.random()*80 + 190, w: 34, h: 34, s: (0.5 + level*0.08)*spd, health: 30*level, max: 30*level }});
                        }}
                    }}
                }});

                if(Math.hypot(p.x - op.x, p.y - op.y) < 26) {{
                    hp -= 0.3;
                    if(hp <= 0) {{ hp = maxHp; score = Math.max(0, score - 30); }}
                }}
            }});

            meats.forEach((m, mi) => {{
                if(Math.hypot(p.x - m.x, p.y - m.y) < 24) {{
                    meats.splice(mi, 1);
                    score += 25;
                    hp = Math.min(maxHp, hp + 25);
                    if(score >= level * 150) {{ level++; p.s += 0.3; }}
                    meats.push({{ x: Math.random()*350 + 180, y: Math.random()*80 + 190, r: 10 }});
                }}
            }});
        }}

        function drawMonkey(x, y, isPlayer) {{
            // Ears
            ctx.fillStyle = "#a04000";
            ctx.fillRect(x - 18, y - 10, 6, 12);
            ctx.fillRect(x + 14, y - 10, 6, 12);

            // Head / Hoodie Helmet (Blue)
            ctx.fillStyle = isPlayer ? "#3498db" : "#e74c3c";
            ctx.fillRect(x - 14, y - 22, 28, 26);

            // Face / Snout (Tan)
            ctx.fillStyle = "#f5b041";
            ctx.fillRect(x - 10, y - 16, 20, 16);

            // Eyes & Angry Brow
            ctx.fillStyle = "#000";
            ctx.fillRect(x - 8, y - 14, 5, 4);
            ctx.fillRect(x + 3, y - 14, 5, 4);

            // Mouth / Teeth
            ctx.fillStyle = "#78281f";
            ctx.fillRect(x - 6, y - 6, 12, 6);

            // Body / Hoodie Torso
            ctx.fillStyle = isPlayer ? "#2980b9" : "#c0392b";
            ctx.fillRect(x - 12, y + 4, 24, 20);

            // Big Boxing Gloves
            ctx.fillStyle = isPlayer ? "#5dade2" : "#95a5a6";
            ctx.fillRect(x - 22, y + 2, 12, 12);
            ctx.fillRect(x + 10, y + 2, 12, 12);
        }}

        function draw() {{
            ctx.clearRect(0, 0, cv.width, cv.height);
            
            // Background Scenery
            ctx.fillStyle = "#5dade2"; ctx.fillRect(0, 0, cv.width, 210);
            ctx.fillStyle = "#27ae60"; ctx.fillRect(0, 210, cv.width, 15);
            ctx.fillStyle = "#784212"; ctx.fillRect(0, 225, cv.width, cv.height - 225);

            // Meats
            meats.forEach(m => {{
                ctx.fillStyle = "#c0392b"; ctx.beginPath(); ctx.arc(m.x, m.y, m.r, 0, Math.PI*2); ctx.fill();
                ctx.fillStyle = "#fff"; ctx.font = "10px sans-serif"; ctx.fillText("🥩", m.x-5, m.y+4);
            }});

            // Bullets
            bullets.forEach(b => {{
                ctx.fillStyle = "#f1c40f"; ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, Math.PI*2); ctx.fill();
            }});

            // Opponent Monkeys
            opponents.forEach(op => {{
                drawMonkey(op.x, op.y, false);
                // Health bar
                ctx.fillStyle = "#333"; ctx.fillRect(op.x - 18, op.y - 34, 36, 4);
                ctx.fillStyle = "#e74c3c"; ctx.fillRect(op.x - 18, op.y - 34, (op.health / op.max) * 36, 4);
            }});

            // Player Monkey
            drawMonkey(p.x, p.y, true);

            // HUD
            ctx.fillStyle = "rgba(0,0,0,0.7)"; ctx.fillRect(10, 10, 290, 32);
            ctx.fillStyle = "#fff"; ctx.font = "11px monospace";
            ctx.fillText(`SCORE: ${{score}} | LVL: ${{level}} | HP: ${{Math.ceil(hp)}}`, 18, 30);
        }}

        function loop() {{ update(); draw(); requestAnimationFrame(loop); }}
        draw();
    </script>
</body>
</html>
"""

st.components.v1.html(game_html, height=450)
