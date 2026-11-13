import streamlit as st

st.set_page_config(
    page_title="Giant Monkey",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: City Brawl")
st.markdown(
    "You are a tiny monkey with heavy-hitting boxing gloves in a massive city. "
    "**Punch opponents** to score points, and **eat meat buffets** to grow in size, heal, and unlock special powers!"
)

# Sidebar controls & instructions
with st.sidebar:
    st.header("🎮 How to Play")
    st.markdown("""
    - **Move:** Arrow Keys or `W`, `A`, `S`, `D`
    - **Punch:** `SPACEBAR`
    - **Objective:** Defeat city opponents and eat meat to level up!
    """)
    st.divider()
    game_speed = st.slider("Game Difficulty / Speed", 1, 3, 2)

# HTML / JS Game embedded via Streamlit Components with a focus handler
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
            background: #2b2b2b;
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
            background: rgba(0,0,0,0.7);
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
            <p>Click to activate controls & start brawl!</p>
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

        // Game State
        let score = 0;
        let level = 1;
        let health = 100;
        let maxHealth = 100;
        let speedMultiplier = {game_speed};

        // Player (Tiny Monkey with Boxing Gloves)
        let player = {{
            x: 350,
            y: 225,
            size: 24,
            speed: 4,
            color: "#e67e22",
            gloveColor: "#e74c3c",
            isPunching: false,
            punchTimer: 0
        }};

        // Opponents & Meat Buffets
        let opponents = [
            {{ x: 100, y: 100, size: 20, speed: 1.5, health: 30 }},
            {{ x: 600, y: 350, size: 22, speed: 1.2, health: 30 }}
        ];

        let meats = [
            {{ x: 200, y: 300, size: 14 }},
            {{ x: 500, y: 120, size: 14 }}
        ];

        let keys = {{}};

        window.addEventListener('keydown', (e) => {{
            if (!gameRunning) return;
            keys[e.code] = true;
            if (e.code === 'Space') {{
                e.preventDefault(); // Prevent page scrolling
                player.isPunching = true;
                player.punchTimer = 10;
                checkCombat();
            }}
        }});

        window.addEventListener('keyup', (e) => {{
            keys[e.code] = false;
        }});

        function checkCombat() {{
            opponents.forEach((op, index) => {{
                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < player.size + op.size + 25) {{
                    op.health -= 15 * level;
                    if (op.health <= 0) {{
                        opponents.splice(index, 1);
                        score += 50;
                        opponents.push({{
                            x: Math.random() * 600 + 50,
                            y: Math.random() * 350 + 50,
                            size: 20,
                            speed: 1 + Math.random() * level,
                            health: 30 * level
                        }});
                    }}
                }}
            }});
        }}

        function update() {{
            if ((keys['ArrowLeft'] || keys['KeyA']) && player.x > player.size) player.x -= player.speed;
            if ((keys['ArrowRight'] || keys['KeyD']) && player.x < canvas.width - player.size) player.x += player.speed;
            if ((keys['ArrowUp'] || keys['KeyW']) && player.y > player.size + 30) player.y -= player.speed;
            if ((keys['ArrowDown'] || keys['KeyS']) && player.y < canvas.height - player.size) player.y += player.speed;

            if (player.punchTimer > 0) player.punchTimer--;
            else player.isPunching = false;

            opponents.forEach(op => {{
                let angle = Math.atan2(player.y - op.y, player.x - op.x);
                op.x += Math.cos(angle) * op.speed * speedMultiplier;
                op.y += Math.sin(angle) * op.speed * speedMultiplier;

                let dist = Math.hypot(player.x - op.x, player.y - op.y);
                if (dist < player.size + op.size) {{
                    health -= 0.3;
                    if (health <= 0) {{
                        health = maxHealth;
                        score = Math.max(0, score - 50);
                    }}
                }}
            }});

            meats.forEach((meat, index) => {{
                let dist = Math.hypot(player.x - meat.x, player.y - meat.y);
                if (dist < player.size + meat.size) {{
                    meats.splice(index, 1);
                    score += 25;
                    health = Math.min(maxHealth, health + 25);
                    
                    if (score >= level * 150) {{
                        level++;
                        player.size += 3;
                        player.speed += 0.5;
                    }}

                    meats.push({{
                        x: Math.random() * 640 + 30,
                        y: Math.random() * 380 + 40,
                        size: 14
                    }});
                }}
            }});
        }}

        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // City Roads Grid
            ctx.strokeStyle = "#383838";
            ctx.lineWidth = 20;
            ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);

            // Meat Buffets
            meats.forEach(meat => {{
                ctx.fillStyle = "#c0392b";
                ctx.beginPath();
                ctx.arc(meat.x, meat.y, meat.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "white";
                ctx.font = "10px sans-serif";
                ctx.fillText("🥩", meat.x - 6, meat.y + 4);
            }});

            // Opponents
            opponents.forEach(op => {{
                ctx.fillStyle = "#7f8c8d";
                ctx.beginPath();
                ctx.arc(op.x, op.y, op.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "white";
                ctx.font = "12px sans-serif";
                ctx.fillText("🤖", op.x - 7, op.y + 4);
            }});

            // Player Monkey
            ctx.fillStyle = player.color;
            ctx.beginPath();
            ctx.arc(player.x, player.y, player.size, 0, Math.PI * 2);
            ctx.fill();

            // Boxing Gloves
            ctx.fillStyle = player.gloveColor;
            let gloveOffset = player.isPunching ? 18 : 10;
            ctx.beginPath();
            ctx.arc(player.x - gloveOffset, player.y - 4, 8, 0, Math.PI * 2);
            ctx.arc(player.x + gloveOffset, player.y - 4, 8, 0, Math.PI * 2);
            ctx.fill();

            // HUD
            ctx.fillStyle = "white";
            ctx.font = "14px sans-serif";
            ctx.fillText(`Score: ${{score}} | Level: ${{level}} | Health: ${{Math.ceil(health)}}/100`, 20, 30);
        }}

        function loop() {{
            update();
            draw();
            requestAnimationFrame(loop);
        }}

        // Initial draw behind overlay
        draw();
    </script>
</body>
</html>
"""

st.components.v1.html(game_html, height=480)
