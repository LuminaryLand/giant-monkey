import streamlit as st

st.set_page_config(
    page_title="Giant Monkey: World Tour",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: World Tour & Super Powers")
st.markdown(
    "Journey through the **City**, **Small Town**, and **Country**! "
    "Shoot rival boxer monkeys directly from your character's gloves, and eat all the meat (🥩) to boost your super powers!"
)

with st.sidebar:
    st.header("🎮 Controls")
    st.markdown("""
    - **Move:** Arrow Keys or `W`, `A`, `S`, `D`
    - **Shoot:** `SPACEBAR`
    - **Objective:** Collect all meat to supercharge fire-rate!
    """)
    st.divider()
    game_speed = st.slider("Game Difficulty / Speed", 1, 3, 1)

game_html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background-color: #111; color: white; font-family: monospace; text-align: center; }
        .container { position: relative; display: inline-block; }
        canvas { background: #5dade2; display: block; margin: 0 auto; border: 4px solid #27ae60; cursor: pointer; image-rendering: pixelated; }
        #overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer; }
        h2 { color: #f1c40f; margin: 0 0 10px 0; }
        p { color: #ddd; font-size: 14px; margin: 0; }
    </style>
</head>
<body>
    <div class="container" onclick="start()">
        <canvas id="cv" width="720" height="420"></canvas>
        <div id="overlay">
            <h2>▶ CLICK TO START GAME</h2>
            <p>Click anywhere to play</p>
        </div>
    </div>
    <script>
        const cv = document.getElementById("cv");
        const ctx = cv.getContext("2d");
        const overlay = document.getElementById("overlay");
        let running = false;
        function start() { if(!running) { running = true; overlay.style.display = "none"; loop(); } }

        let score = 0, level = 1, hp = 100, maxHp = 100, spd = __GAME_SPEED__;
        let cameraX = 0;
        let powerLevel = 1;
        let lastShotTime = 0;
        
        let p = { x: 120, y: 260, w: 36, h: 36, s: 3.5 };
        let bullets = [];
        
        let opponents = [
            { x: 550, y: 260, health: 30, max: 30, speed: 0.8 },
            { x: 900, y: 270, health: 30, max: 30, speed: 0.7 },
            { x: 1300, y: 250, health: 40, max: 40, speed: 0.9 }
        ];

        let meats = [
            { x: 380, y: 275, r: 24 },
            { x: 720, y: 265, r: 24 },
            { x: 1080, y: 280, r: 24 }
        ];

        let keys = {};

        window.addEventListener('keydown', e => {
            if(!running) return;
            keys[e.code] = true;
            if(e.code === 'Space') {
                e.preventDefault();
                let now = Date.now();
                let fireCooldown = Math.max(100, 320 - (powerLevel * 45));
                
                if (now - lastShotTime > fireCooldown) {
                    // Shoot directly from the tip of the player's front boxing glove (x + 24)
                    bullets.push({ 
                        x: p.x + 26, 
                        y: p.y + 4, 
                        s: 8 + (powerLevel * 0.4), 
                        r: 5 + Math.min(powerLevel, 3) 
                    });
                    lastShotTime = now;
                }
            }
        });
        window.addEventListener('keyup', e => { keys[e.code] = false; });

        function getEnvironmentName() {
            if (level === 1) return "LEVEL 1: CITY";
            if (level === 2) return "LEVEL 2: SMALL TOWN";
            return "LEVEL 3: COUNTRY";
        }

        function update() {
            if ((keys['ArrowLeft'] || keys['KeyA']) && p.x > 50) p.x -= p.s;
            if ((keys['ArrowRight'] || keys['KeyD'])) {
                p.x += p.s;
                cameraX += p.s * 0.5;
            }
            if ((keys['ArrowUp'] || keys['KeyW']) && p.y > 210) p.y -= p.s;
            if ((keys['ArrowDown'] || keys['KeyS']) && p.y < cv.height - 75) p.y += p.s;

            // Bullets update
            bullets.forEach((b, i) => {
                b.x += b.s;
                if (b.x > cv.width + cameraX) bullets.splice(i, 1);
            });

            // Opponents update
            opponents.forEach((op, idx) => {
                op.x -= op.speed * spd;

                if (op.x < cameraX - 100) {
                    op.x = cameraX + cv.width + Math.random() * 200;
                    op.y = Math.random() * 80 + 210;
                }

                bullets.forEach((b, bi) => {
                    if (Math.hypot(b.x - op.x, b.y - op.y) < 28) {
                        op.health -= (15 + (powerLevel * 5));
                        bullets.splice(bi, 1);
                        if (op.health <= 0) {
                            opponents.splice(idx, 1);
                            score += 60;
                            
                            opponents.push({
                                x: cameraX + cv.width + Math.random() * 200,
                                y: Math.random() * 80 + 210,
                                health: 30 * level,
                                max: 30 * level,
                                speed: 0.7 + (level * 0.1)
                            });

                            if (score >= level * 200) {
                                level++;
                                hp = maxHp;
                            }
                        }
                    }
                });

                if (Math.hypot(p.x - op.x, p.y - op.y) < 28) {
                    hp -= 0.35;
                    if (hp <= 0) {
                        hp = maxHp;
                        score = Math.max(0, score - 40);
                    }
                }
            });

            // Meat Collection (Expanded hit-box distance so it's easy to eat)
            meats.forEach((m, mi) => {
                let worldDist = Math.abs(p.x - m.x);
                if (worldDist < 35 && Math.abs(p.y - m.y) < 35) {
                    meats.splice(mi, 1);
                    score += 40;
                    hp = Math.min(maxHp, hp + 35);
                    powerLevel++; // Super power up!

                    meats.push({
                        x: cameraX + cv.width + Math.random() * 300,
                        y: Math.random() * 80 + 210,
                        r: 24
                    });
                }
            });
        }

        function drawScenery() {
            if (level === 1) {
                ctx.fillStyle = "#2c3e50"; ctx.fillRect(0, 0, cv.width, 210);
                ctx.fillStyle = "#34495e";
                ctx.fillRect(50 - (cameraX * 0.2) % 800, 60, 100, 150);
                ctx.fillRect(180 - (cameraX * 0.2) % 800, 30, 120, 180);
                ctx.fillRect(350 - (cameraX * 0.2) % 800, 80, 90, 130);
            } else if (level === 2) {
                ctx.fillStyle = "#5dade2"; ctx.fillRect(0, 0, cv.width, 210);
                ctx.fillStyle = "#d35400";
                ctx.fillRect(60 - (cameraX * 0.3) % 700, 100, 140, 110);
                ctx.fillRect(280 - (cameraX * 0.3) % 700, 90, 160, 120);
            } else {
                ctx.fillStyle = "#85c1e9"; ctx.fillRect(0, 0, cv.width, 210);
                ctx.fillStyle = "#27ae60";
                ctx.beginPath();
                ctx.arc(300 - (cameraX * 0.4) % 900, 210, 180, Math.PI, 0, false);
                ctx.arc(750 - (cameraX * 0.4) % 900, 210, 220, Math.PI, 0, false);
                ctx.fill();
            }

            ctx.fillStyle = level === 1 ? "#7f8c8d" : (level === 2 ? "#d68910" : "#229954");
            ctx.fillRect(0, 210, cv.width, 15);
            ctx.fillStyle = level === 1 ? "#34495e" : (level === 2 ? "#7e5109" : "#145a32");
            ctx.fillRect(0, 225, cv.width, cv.height - 225);
        }

        function drawMonkey(x, y, isPlayer) {
            ctx.fillStyle = "#a04000";
            ctx.fillRect(x - 18, y - 10, 6, 12);
            ctx.fillRect(x + 14, y - 10, 6, 12);

            ctx.fillStyle = isPlayer ? "#3498db" : "#e74c3c";
            ctx.fillRect(x - 14, y - 22, 28, 26);

            ctx.fillStyle = "#f5b041";
            ctx.fillRect(x - 10, y - 16, 20, 16);

            ctx.fillStyle = "#000";
            ctx.fillRect(x - 8, y - 14, 5, 4);
            ctx.fillRect(x + 3, y - 14, 5, 4);

            ctx.fillStyle = "#78281f";
            ctx.fillRect(x - 6, y - 6, 12, 6);

            ctx.fillStyle = isPlayer ? "#2980b9" : "#c0392b";
            ctx.fillRect(x - 12, y + 4, 24, 20);

            // Boxing Gloves
            ctx.fillStyle = isPlayer ? "#5dade2" : "#95a5a6";
            ctx.fillRect(x - 22, y + 2, 12, 12);
            ctx.fillRect(x + 14, y + 2, 12, 12); // Right glove where bullets launch from
        }

        function draw() {
            ctx.clearRect(0, 0, cv.width, cv.height);
            drawScenery();

            meats.forEach(m => {
                let screenX = m.x - cameraX;
                if (screenX > -60 && screenX < cv.width + 60) {
                    ctx.fillStyle = "#c0392b"; ctx.beginPath(); ctx.arc(screenX, m.y, 14, 0, Math.PI*2); ctx.fill();
                    ctx.fillStyle = "#fff"; ctx.font = "12px sans-serif"; ctx.fillText("🥩", screenX-7, m.y+5);
                }
            });

            bullets.forEach(b => {
                let screenX = b.x - cameraX;
                ctx.fillStyle = "#f1c40f"; ctx.beginPath(); ctx.arc(screenX, b.y, b.r, 0, Math.PI*2); ctx.fill();
            });

            opponents.forEach(op => {
                let screenX = op.x - cameraX;
                if (screenX > -60 && screenX < cv.width + 60) {
                    drawMonkey(screenX, op.y, false);
                    ctx.fillStyle = "#333"; ctx.fillRect(screenX - 18, op.y - 34, 36, 4);
                    ctx.fillStyle = "#e74c3c"; ctx.fillRect(screenX - 18, op.y - 34, (op.health / op.max) * 36, 4);
                }
            });

            drawMonkey(p.x, p.y, true);

            ctx.fillStyle = "rgba(0,0,0,0.75)"; ctx.fillRect(10, 10, 410, 42);
            ctx.strokeStyle = "#f1c40f"; ctx.lineWidth = 2; ctx.strokeRect(10, 10, 410, 42);
            
            ctx.fillStyle = "#fff"; ctx.font = "11px monospace";
            ctx.fillText(`${getEnvironmentName()} | SUPER POWER LVL: ${powerLevel}`, 18, 25);
            ctx.fillText(`SCORE: ${score} | HP: ${Math.ceil(hp)}`, 18, 42);
        }

        function loop() { update(); draw(); requestAnimationFrame(loop); }
        draw();
    </script>
</body>
</html>
"""

game_html = game_html_template.replace("__GAME_SPEED__", str(game_speed))

st.components.v1.html(game_html, height=450)
