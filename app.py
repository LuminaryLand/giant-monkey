import streamlit as st

st.set_page_config(
    page_title="Giant Monkey: Town Brawl",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: Town Brawl")
st.markdown(
    "You are a tiny monkey with heavy boxing gloves in a town. "
    "**Punch (SPACE)** and **Kick (K)** incoming opponents, and **eat meat (🥩)** to grow and level up!"
)

# Sidebar controls & instructions
with st.sidebar:
    st.header("🎮 Controls")
    st.markdown("""
    - **Move:** Arrow Keys or `W`, `A`, `S`, `D`
    - **Punch:** `SPACEBAR`
    - **Kick:** `K` or `X`
    - **Objective:** Fight attackers & eat meat to level up!
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
            background-color: #1a1a1a;
            color: white;
            font-family: sans-serif;
            text-align: center;
        }}
        .game-container {{
            position: relative;
            display: inline-block;
        }}
        canvas {{
            background: #3d3d3d;
            display: block;
            margin: 0 auto;
            border: 4px solid #f39c12;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.5);
            cursor: pointer;
        }}
        #overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.75);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border-radius: 8px;
            cursor: pointer;
        }}
        h2 {{ margin: 0 0 10px 0; color: #f39c12; }}
        p {{ margin: 0; font-size: 14px; color: #ddd; }}
    </style>
</head>
<body>
    <div class="game-container" onclick="startGame()">
        <canvas id="gameCanvas" width="700" height="450"></canvas>
        <div id="overlay">
            <h2>▶ Click Here to Play</h2>
            <p>Click to activate controls & start town brawl!</p>
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

        // Player Monkey Character
        let player = {{
            x: 350,
            y: 225,
            size: 18,
            speed: 4,
            isPunching: false,
            punchTimer: 0,
            isKicking: false,
            kickTimer: 0
        }};

        let opponents = [
            {{ x: 100, y: 100, size: 16, speed: 1.5, health: 30 }},
            {{ x: 600, y: 350, size: 18, speed: 1.2, health: 30 }}
        ];

        let meats = [
            {{ x: 200, y: 300, size: 12 }},
            {{ x: 500, y: 120, size: 12 }}
        ];

        let keys = {{}};

        window.addEventListener('keydown', (e) => {{
            if (!gameRunning) return;
            keys[e.code] = true;
            
            if (e.code === 'Space') {{
                e.preventDefault();
                player.isPunching = true;
                player.punchTimer = 12;
                checkCombat(20);
            }}
            if (e.code === 'KeyK' || e.code === 'KeyX') {{
                e.preventDefault();
                player.isKicking = true;
                player.kickTimer = 12;
                checkCombat(30);
            }}
        }});

        window.addEventListener('keyup', (e) => {{
            keys[e.code] = false;
        }});

        function checkCombat(damage) {{
            opponents.forEach((op, index) => {{
                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < 45 + player.size) {{
                    op.health -= damage * level;
                    if (op.health <= 0) {{
                        opponents.splice(index, 1);
                        score += 50;
                        opponents.push({{
                            x: Math.random() * 600 + 50,
                            y: Math.random() * 350 + 50,
                            size: 16,
                            speed: 1 + Math.random() * level,
                            health: 30 * level
                        }});
                    }}
                }}
            }});
        }}

        function update() {{
            if ((keys['ArrowLeft'] || keys['KeyA']) && player.x > 30) player.x -= player.speed;
            if ((keys['ArrowRight'] || keys['KeyD']) && player.x < canvas.width - 30) player.x += player.speed;
            if ((keys['ArrowUp'] || keys['KeyW']) && player.y > 40) player.y -= player.speed;
            if ((keys['ArrowDown'] || keys['KeyS']) && player.y < canvas.height - 30) player.y += player.speed;

            if (player.punchTimer > 0) player.punchTimer--;
            else player.isPunching = false;

            if (player.kickTimer > 0) player.kickTimer--;
            else player.isKicking = false;

            // Opponents chase player
            opponents.forEach(op => {{
                let angle = Math.atan2(player.y - op.y, player.x - op.x);
                op.x += Math.cos(angle) * op.speed * speedMultiplier;
                op.y += Math.sin(angle) * op.speed * speedMultiplier;

                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < player.size + op.size + 5) {{
                    health -= 0.35;
                    if (health <= 0) {{
                        health = maxHealth;
                        score = Math.max(0, score - 50);
                    }}
                }}
            }});

            // Meat collection
            meats.forEach((meat, index) => {{
                let dist = Math.hypot(player.x - meat.x, player.y - meat.y);
                if (dist < player.size + meat.size + 10) {{
                    meats.splice(index, 1);
                    score += 25;
                    health = Math.min(maxHealth, health + 30);
                    
                    if (score >= level * 150) {{
                        level++;
                        player.size += 2;
                        player.speed += 0.4;
                    }}

                    meats.push({{
                        x: Math.random() * 640 + 30,
                        y: Math.random() * 380 + 40,
                        size: 12
                    }});
                }}
            }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Town cobblestone background grid lines
            ctx.strokeStyle = "#4a4a4a";
            ctx.lineWidth = 15;
            ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);

            // Draw Meat Buffets
            meats.forEach(meat => {{
                ctx.fillStyle = "#e74c3c";
                ctx.beginPath();
                ctx.arc(meat.x, meat.y, meat.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#fff";
                ctx.font = "12px sans-serif";
                ctx.fillText("🥩", meat.x - 7, meat.y + 4);
            }});

            // Draw Opponents (Attackers)
            opponents.forEach(op => {{
                ctx.fillStyle = "#95a5a6";
                ctx.beginPath();
                ctx.arc(op.x, op.y - 4, op.size, 0, Math.PI * 2);
                ctx.fill();
                // Opponent head & visor
                ctx.fillStyle = "#34495e";
                ctx.fillRect(op.x - 8, op.y - 14, 16, 10);
            }});

            // --- DRAW PLAYER MONKEY CHARACTER ---
            let pSize = player.size;
            
            // Tail
            ctx.strokeStyle = "#b5651d";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(player.x - pSize, player.y + 5);
            ctx.quadraticCurveTo(player.x - pSize - 18, player.y + 15, player.x - pSize - 10, player.y - 10);
            ctx.stroke();

            // Body / Torso (Fur brown)
            ctx.fillStyle = "#d35400";
            ctx.beginPath();
            ctx.arc(player.x, player.y, pSize, 0, Math.PI * 2);
            ctx.fill();

            // Head & Face (Tan snout area)
            ctx.fillStyle = "#e59866";
            ctx.beginPath();
            ctx.arc(player.x, player.y - pSize - 4, pSize * 0.8, 0, Math.PI * 2);
            ctx.fill();

            // Ears
            ctx.fillStyle = "#d35400";
            ctx.beginPath();
            ctx.arc(player.x - pSize * 0.7, player.y - pSize - 4, 6, 0, Math.PI * 2);
            ctx.arc(player.x + pSize * 0.7, player.y - pSize - 4, 6, 0, Math.PI * 2);
            ctx.fill();

            // Eyes (Angry fighter expression)
            ctx.fillStyle = "#000";
            ctx.fillRect(player.x - 6, player.y - pSize - 8, 4, 3);
            ctx.fillRect(player.x + 2, player.y - pSize - 8, 4, 3);

            // Big Red Boxing Gloves
            ctx.fillStyle = "#c0392b";
            let leftGloveX = player.x - pSize - (player.isPunching ? 16 : 8);
            let rightGloveX = player.x + pSize + (player.isPunching ? 16 : 8);
            
            ctx.beginPath();
            ctx.arc(leftGloveX, player.y - 2, 9, 0, Math.PI * 2);
            ctx.arc(rightGloveX, player.y - 2, 9, 0, Math.PI * 2);
            ctx.fill();

            // Kicking Foot Animation
            if (player.isKicking) {{
                ctx.fillStyle = "#78281f";
                ctx.fillRect(player.x + pSize, player.y + pSize - 2, 16, 8);
            }}

            // HUD Overlay
            ctx.fillStyle = "white";
            ctx.font = "14px sans-serif";
            ctx.fillText(`Score: ${{score}} | Level: ${{level}} | Health: ${{Math.ceil(health)}}/100`, 20, 30);
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        draw();
    </script>
</body>
</html>
"""

st.components.v1.html(game_html, height=480)
