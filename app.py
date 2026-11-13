import streamlit as st

st.set_page_config(
    page_title="Giant Monkey: Retro Beat-Down",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: Retro Town Brawl")
st.markdown(
    "Control your retro boxing monkey, fight oncoming street opponents, and eat meat buffets to level up!"
)

with st.sidebar:
    st.header("🎮 Retro Controls")
    st.markdown("""
    - **Move:** Arrow Keys or `W`, `A`, `S`, `D`
    - **Punch:** `SPACEBAR`
    - **Kick:** `K` or `X`
    - **Objective:** Defeat waves of fighters & eat meat!
    """)
    st.divider()
    game_speed = st.slider("Game Difficulty / Speed", 1, 3, 2)

game_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            margin: 0;
            background-color: #0d0d0d;
            color: white;
            font-family: 'Courier New', monospace;
            text-align: center;
        }}
        .game-container {{
            position: relative;
            display: inline-block;
        }}
        canvas {{
            background: #1e3d59;
            display: block;
            margin: 0 auto;
            border: 4px solid #f39c12;
            box-shadow: 0 8px 24px rgba(0,0,0,0.8);
            image-rendering: pixelated;
            cursor: pointer;
        }}
        #overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
        }}
        h2 {{ color: #f39c12; margin-bottom: 5px; }}
        p {{ color: #ddd; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="game-container" onclick="startGame()">
        <canvas id="gameCanvas" width="720" height="480"></canvas>
        <div id="overlay">
            <h2>▶ CLICK TO START RETRO BRAWL</h2>
            <p>Click anywhere to activate arcade controls</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const overlay = document.getElementById("overlay");

        let gameRunning = false;

        function startGame() {{
            if (!gameRunning) {{
                gameRunning = true;
                overlay.style.display = "none";
                loop();
            }}
        }}

        let score = 0;
        let level = 1;
        let health = 100;
        let maxHealth = 100;
        let speedMultiplier = {game_speed};

        let player = {{
            x: 360,
            y: 280,
            width: 32,
            height: 40,
            speed: 4,
            isPunching: false,
            punchTimer: 0,
            isKicking: false,
            kickTimer: 0
        }};

        let opponents = [
            {{ x: 100, y: 260, width: 30, height: 38, speed: 1.2, health: 40, maxHealth: 40 }},
            {{ x: 620, y: 300, width: 30, height: 38, speed: 1.0, health: 40, maxHealth: 40 }}
        ];

        let meats = [
            {{ x: 220, y: 320, size: 12 }},
            {{ x: 500, y: 240, size: 12 }}
        ];

        let keys = {{}};

        window.addEventListener('keydown', (e) => {{
            if (!gameRunning) return;
            keys[e.code] = true;
            if (e.code === 'Space') {{
                e.preventDefault();
                player.isPunching = true;
                player.punchTimer = 10;
                checkCombat(25);
            }}
            if (e.code === 'KeyK' || e.code === 'KeyX') {{
                e.preventDefault();
                player.isKicking = true;
                player.kickTimer = 10;
                checkCombat(35);
            }}
        }});

        window.addEventListener('keyup', (e) => {{
            keys[e.code] = false;
        }});

        function checkCombat(damage) {{
            opponents.forEach((op, index) => {{
                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < 50) {{
                    op.health -= damage;
                    if (op.health <= 0) {{
                        opponents.splice(index, 1);
                        score += 100;
                        opponents.push({{
                            x: Math.random() > 0.5 ? 50 : 650,
                            y: Math.random() * 120 + 220,
                            width: 30,
                            height: 38,
                            speed: 1.2 + (level * 0.2),
                            health: 40 * level,
                            maxHealth: 40 * level
                        }});
                    }}
                }}
            }});
        }}

        function update() {{
            if ((keys['ArrowLeft'] || keys['KeyA']) && player.x > 40) player.x -= player.speed;
            if ((keys['ArrowRight'] || keys['KeyD']) && player.x < canvas.width - 40) player.x += player.speed;
            if ((keys['ArrowUp'] || keys['KeyW']) && player.y > 200) player.y -= player.speed;
            if ((keys['ArrowDown'] || keys['KeyS']) && player.y < canvas.height - 90) player.y += player.speed;

            if (player.punchTimer > 0) player.punchTimer--;
            else player.isPunching = false;

            if (player.kickTimer > 0) player.kickTimer--;
            else player.isKicking = false;

            opponents.forEach(op => {{
                let angle = Math.atan2(player.y - op.y, player.x - op.x);
                op.x += Math.cos(angle) * op.speed * speedMultiplier;
                op.y += Math.sin(angle) * op.speed * speedMultiplier;

                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < 35) {{
                    health -= 0.4;
                    if (health <= 0) {{
                        health = maxHealth;
                        score = Math.max(0, score - 100);
                    }}
                }}
            }});

            meats.forEach((meat, index) => {{
                let dist = Math.hypot(player.x - meat.x, player.y - meat.y);
                if (dist < 30) {{
                    meats.splice(index, 1);
                    score += 50;
                    health = Math.min(maxHealth, health + 35);

                    if (score >= level * 200) {{
                        level++;
                        player.speed += 0.3;
                    }}

                    meats.push({{
                        x: Math.random() * 600 + 60,
                        y: Math.random() * 140 + 210,
                        size: 12
                    }});
                }}
            }});
        }}

        function drawBackground() {{
            // Retro Sky / Industrial City Backdrop
            ctx.fillStyle = "#111b21";
            ctx.fillRect(0, 0, canvas.width, 180);

            // Warehouse / Building silhouettes
            ctx.fillStyle = "#222e35";
            ctx.fillRect(50, 40, 160, 140);
            ctx.fillRect(260, 20, 200, 160);
            ctx.fillRect(500, 60, 180, 120);

            // Industrial Pipes
            ctx.fillStyle = "#d35400";
            ctx.fillRect(100, 0, 16, 180);
            ctx.fillRect(320, 0, 20, 180);
            ctx.fillRect(580, 0, 16, 180);

            // Chain-link fence barrier
            ctx.fillStyle = "#4e5d6c";
            ctx.fillRect(0, 175, canvas.width, 15);

            // Fighting Arena Floor (Blue tile floor style)
            ctx.fillStyle = "#2980b9";
            ctx.fillRect(0, 190, canvas.width, canvas.height - 190);
            
            // Floor grid perspective lines
            ctx.strokeStyle = "#1f618d";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(180, 190); ctx.lineTo(80, canvas.height);
            ctx.moveTo(540, 190); ctx.lineTo(640, canvas.height);
            ctx.stroke();
        }}

        function drawHUD() {{
            // NES Bottom Panel Box
            ctx.fillStyle = "#000000";
            ctx.fillRect(0, canvas.height - 75, canvas.width, 75);
            ctx.strokeStyle = "#f39c12";
            ctx.lineWidth = 3;
            ctx.strokeRect(0, canvas.height - 75, canvas.width, 75);

            // 1P Panel
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 12px 'Courier New'";
            ctx.fillText("1P MONKEY", 20, canvas.height - 50);
            ctx.fillText(`LVL ${level}`, 140, canvas.height - 50);

            // Player Health Bar Background & Fill
            ctx.fillStyle = "#555";
            ctx.fillRect(20, canvas.height - 40, 150, 12);
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(20, canvas.height - 40, (health / maxHealth) * 150, 12);

            // Score / Status Panel
            ctx.fillText(`SCORE: ${score}`, 240, canvas.height - 50);
            ctx.fillText(`MEAT BUFF: ACTIVE`, 240, canvas.height - 25);

            // CPU Opponents Panel
            ctx.fillText("CPU OPPONENTS", 480, canvas.height - 50);
            ctx.fillStyle = "#555";
            ctx.fillRect(480, canvas.height - 40, 180, 12);
            let totalOpHealth = opponents.reduce((acc, op) => acc + op.health, 0);
            let maxOpHealth = opponents.reduce((acc, op) => acc + op.maxHealth, 0);
            ctx.fillStyle = "#f1c40f";
            ctx.fillRect(480, canvas.height - 40, Math.max(0, (totalOpHealth / maxOpHealth) * 180), 12);
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawBackground();

            // Draw Meat Buffs
            meats.forEach(meat => {{
                ctx.fillStyle = "#c0392b";
                ctx.beginPath();
                ctx.arc(meat.x, meat.y, meat.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#ffffff";
                ctx.font = "10px sans-serif";
                ctx.fillText("🥩", meat.x - 6, meat.y + 4);
            }});

            // Draw Opponents
            opponents.forEach(op => {{
                ctx.fillStyle = "#e
