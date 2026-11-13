import streamlit as st

st.set_page_config(
    page_title="Giant Monkey: Jungle Shootout",
    page_icon="🦍",
    layout="centered"
)

st.title("🦍 Giant Monkey: Jungle Shootout")
st.markdown(
    "Shoot projectiles at incoming rival monkeys, eat meat buffets (🥩) to level up, and survive the jungle!"
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

game_html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            background-color: #111;
            color: white;
            font-family: 'Courier New', monospace;
            text-align: center;
        }
        .game-container {
            position: relative;
            display: inline-block;
        }
        canvas {
            background: #4aa3df;
            display: block;
            margin: 0 auto;
            border: 4px solid #27ae60;
            box-shadow: 0 8px 24px rgba(0,0,0,0.8);
            image-rendering: pixelated;
            cursor: pointer;
        }
        #overlay {
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
        }
        h2 { color: #f1c40f; margin-bottom: 5px; }
        p { color: #ddd; font-size: 14px; }
    </style>
</head>
<body>
    <div class="game-container" onclick="startGame()">
        <canvas id="gameCanvas" width="720" height="420"></canvas>
        <div id="overlay">
            <h2>▶ CLICK TO START JUNGLE SHOOTOUT</h2>
            <p>Click anywhere to play</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const overlay = document.getElementById("overlay");

        let gameRunning = false;

        function startGame() {
            if (!gameRunning) {
                gameRunning = true;
                overlay.style.display = "none";
                loop();
            }
        }

        let score = 0;
        let level = 1;
        let health = 100;
        let maxHealth = 100;
        let baseSpeed = __GAME_SPEED__;

        // Player Monkey
        let player = {
            x: 100,
            y: 260,
            width: 36,
            height: 38,
            speed: 3.5
        };

        // Projectiles (Bullets)
        let bullets = [];

        // Opponents (Rival Monkeys moving slower from the right)
        let opponents = [
            { x: 600, y: 260, width: 34, height: 36, speed: 0.8 * baseSpeed, health: 30, maxHealth: 30 },
            { x: 750, y: 280, width: 34, height: 36, speed: 0.7 * baseSpeed, health: 30, maxHealth: 30 }
        ];

        // Meat Buffets
        let meats = [
            { x: 350, y: 290, size: 12 },
            { x: 500, y: 250, size: 12 }
        ];

        let keys = {};

        window.addEventListener('keydown', (e) => {
            if (!gameRunning) return;
            keys[e.code] = true;
            if (e.code === 'Space') {
                e.preventDefault();
                // Shoot projectile from player position
                bullets.push({
                    x: player.x + player.width,
                    y: player.y + 12,
                    speed: 7,
                    size: 6
                });
            }
        });

        window.addEventListener('keyup', (e) => {
            keys[e.code] = false;
        });

        function update() {
            // Movement
            if ((keys['ArrowLeft'] || keys['KeyA']) && player.x > 30) player.x -= player.speed;
            if ((keys['ArrowRight'] || keys['KeyD']) && player.x < canvas.width / 2) player.x += player.speed;
            if ((keys['ArrowUp'] || keys['KeyW']) && player.y > 210) player.y -= player.speed;
            if ((keys['ArrowDown'] || keys['KeyS']) && player.y < canvas.height - 90) player.y += player.speed;

            // Update Bullets
            bullets.forEach((b, index) => {
                b.x += b.speed;
                if (b.x > canvas.width) {
                    bullets.splice(index, 1);
                }
            });

            // Update Opponents (Rival Monkeys)
            opponents.forEach((op, opIndex) => {
                // Walk slowly towards player
                op.x -= op.speed;

                // Reset opponent if they pass left side
                if (op.x < -40) {
                    op.x = canvas.width + 50;
                    op.y = Math.random() * 80 + 220;
                }

                // Check bullet collisions with opponent
                bullets.forEach((b, bIndex) => {
                    let dist = Math.hypot(b.x - op.x, b.y - op.y);
                    if (dist < 25) {
                        op.health -= 15;
                        bullets.splice(bIndex, 1);
                        if (op.health <= 0) {
                            opponents.splice(opIndex, 1);
                            score += 50;
                            // Spawn new rival monkey
                            opponents.push({
                                x: canvas.width + 60,
                                y: Math.random() * 80 + 220,
                                width: 34,
                                height: 36,
                                speed: (0.7 + (level * 0.1)) * baseSpeed,
                                health: 30 * level,
                                maxHealth: 30 * level
                            });
                        }
                    }
                });

                // Check player contact damage
                let pDist = Math.hypot(player.x - op.x, player.y - op.y);
                if (pDist < 30) {
                    health -= 0.3;
                    if (health <= 0) {
                        health = maxHealth;
                        score = Math.max(0, score - 50);
                    }
                }
            });

            // Update Meats
            meats.forEach((meat, index) => {
                let dist = Math.hypot(player.x - meat.x, player.y - meat.y);
                if (dist < 25) {
                    meats.splice(index, 1);
                    score += 25;
                    health = Math.min(maxHealth, health + 30);

                    if (score >= level * 150) {
                        level++;
                        player.speed += 0.3;
                    }

                    meats.push({
                        x: Math.random() * 400 + 200,
                        y: Math.random() * 80 + 220,
                        size: 12
                    });
                }
            });
        }

        function drawScenery() {
            // Sky
            ctx.fillStyle = "#5dade2";
            ctx.fillRect(0, 0, canvas.width, 240);

            // Clouds
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(100, 40, 70, 24);
            ctx.fillRect(450, 70, 90, 28);

            // Jungle Green Ground
            ctx.fillStyle = "#27ae60";
            ctx.fillRect(0, 240, canvas.width, 20);

            // Brown Dirt Ground
            ctx.fillStyle = "#784212";
            ctx.fillRect(0, 260, canvas.width, canvas.height - 260);

            // Grass tufts
            ctx.fillStyle = "#2ecc71";
            for (let i = 0; i < canvas.width; i += 30) {
                ctx.fillRect(i, 235, 10, 8);
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawScenery();

            // Draw Meat Buffets
            meats.forEach(meat => {
                ctx.fillStyle = "#c0392b";
                ctx.beginPath();
                ctx.arc(meat.x, meat.y, meat.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#fff";
                ctx.font = "10px sans-serif";
                ctx.fillText("🥩", meat.x - 6, meat.y + 4);
            });

            // Draw Bullets
            bullets.forEach(b => {
                ctx.fillStyle = "#f1c40f";
                ctx.beginPath();
                ctx.arc(b.x, b.y, b.size, 0, Math.PI * 2);
                ctx.fill();
            });

            // Draw Opponent Rival Monkeys
            opponents.forEach(op => {
                // Rival Monkey Body
                ctx.fillStyle = "#a04000";
                ctx.fillRect(op.x - 14, op.y - 20, 28, 26);
                // Head
                ctx.fillStyle = "#d35400";
                ctx.beginPath();
                ctx.arc(op.x, op.y - 28, 11, 0, Math.PI * 2);
                ctx.fill();
                // Face snout
                ctx.fillStyle = "#f39c12";
                ctx.fillRect(op.x - 6, op.y - 32, 12, 10);

                // Health bar above rival
                ctx.fillStyle = "#333";
                ctx.fillRect(op.x - 18, op.y - 48, 36, 5);
                ctx.fillStyle = "#e74c3c";
                ctx.fillRect(op.x - 18, op.y - 48, (op.health / op.maxHealth) * 36, 5);
            });

            // Draw Player Giant Monkey
            let p = player;
            // Tail
            ctx.strokeStyle = "#873600";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(p.x - 16, p.y - 10);
            ctx.quadraticCurveTo(p.x - 30, p.y + 10, p.x - 20, p.y + 18);
            ctx.stroke();

            // Body
            ctx.fillStyle = "#b9770e";
            ctx.fillRect(p.x - 16, p.y - 24, 32, 30);

            // Head & Snout
            ctx.fillStyle = "#f39c12";
            ctx.fillRect(p.x - 12, p.y - 40, 24, 18);

            // Ears
            ctx.fillStyle = "#873600";
            ctx.fillRect(p.x - 20, p.y - 36, 8, 10);
            ctx.fillRect(p.x + 12, p.y
