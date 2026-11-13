import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Giant Monkey: Metal Slug World Tour",
    page_icon="🦍",
    layout="wide"
)

st.title("🦍 Giant Monkey: Metal Slug Edition")
st.markdown("Run, jump, and shoot your way through retro stages as a classic pixel-art style combat monkey!")

# HTML/JS Game Component
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            margin: 0; 
            background: #1a1a1a; 
            color: #fff; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
        }
        canvas { 
            background: linear-gradient(to bottom, #3a6073, #16222a); 
            display: block; 
            margin: 15px auto; 
            border: 3px solid #555; 
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
        }
        #ui { 
            font-size: 20px; 
            font-weight: bold; 
            letter-spacing: 1px;
            margin-top: 10px;
        }
        #controls-hint {
            font-size: 14px;
            color: #aaa;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div id="ui">Stage: <span id="stageDisplay">1 - City Slums</span> | Score: <span id="scoreDisplay">0</span> | HP: <span id="hpDisplay">♥♥♥</span></div>
    <div id="controls-hint">Controls: A/D or Left/Right to Move | W or Space to Jump | J or Click to Shoot Bananas</div>
    <canvas id="gameCanvas" width="800" height="450"></canvas>
    
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Game State
        let score = 0;
        let hp = 3;
        let stage = 1;
        let stageName = "City Slums";
        let cameraX = 0;

        // Player (Retro Pixel Monkey)
        let player = {
            x: 100,
            y: 300,
            width: 44,
            height: 52,
            vx: 0,
            vy: 0,
            speed: 4,
            jumpForce: -11,
            gravity: 0.5,
            grounded: false,
            facing: 1 // 1 = right, -1 = left
        };

        let keys = {};
        let bullets = [];
        let enemies = [
            { x: 600, y: 330, width: 40, height: 50, vx: -1.5, hp: 2, type: "mercenary" },
            { x: 950, y: 330, width: 40, height: 50, vx: -2, hp: 3, type: "mercenary" },
            { x: 1400, y: 320, width: 50, height: 60, vx: -1, hp: 5, type: "heavy" }
        ];

        window.addEventListener("keydown", (e) => { 
            keys[e.key.toLowerCase()] = true; 
            if ((e.key === " " || e.key.toLowerCase() === "w") && player.grounded) {
                player.vy = player.jumpForce;
                player.grounded = false;
            }
            if (e.key.toLowerCase() === "j" || e.key === " ") {
                shootBullet();
            }
        });

        window.addEventListener("keyup", (e) => { 
            keys[e.key.toLowerCase()] = false; 
        });

        function shootBullet() {
            bullets.push({
                x: player.facing > 0 ? player.x + player.width : player.x - 10,
                y: player.y + 20,
                vx: player.facing * 9,
                radius: 6
            });
        }

        function update() {
            // Horizontal Movement
            player.vx = 0;
            if (keys["a"] || keys["arrowleft"]) {
                player.vx = -player.speed;
                player.facing = -1;
            }
            if (keys["d"] || keys["arrowright"]) {
                player.vx = player.speed;
                player.facing = 1;
            }

            player.x += player.vx;
            if (player.x < cameraX + 50) player.x = cameraX + 50; // Don't run off left screen

            // Gravity & Vertical Physics
            player.vy += player.gravity;
            player.y += player.vy;

            // Ground collision
            const groundLevel = 350;
            if (player.y + player.height >= groundLevel) {
                player.y = groundLevel - player.height;
                player.vy = 0;
                player.grounded = true;
            }

            // Camera follow player forward
            if (player.x > cameraX + 300) {
                cameraX = player.x - 300;
            }

            // Update Bullets
            for (let i = bullets.length - 1; i >= 0; i--) {
                bullets[i].x += bullets[i].vx;
                // Remove out of bounds
                if (bullets[i].x > cameraX + 850 || bullets[i].x < cameraX - 50) {
                    bullets.splice(i, 1);
                    continue;
                }

                // Check collision with enemies
                for (let j = enemies.length - 1; j >= 0; j--) {
                    let en = enemies[j];
                    if (
                        bullets[i] &&
                        bullets[i].x > en.x && 
                        bullets[i].x < en.x + en.width &&
                        bullets[i].y > en.y && 
                        bullets[i].y < en.y + en.height
                    ) {
                        en.hp--;
                        bullets.splice(i, 1);
                        if (en.hp <= 0) {
                            score += 100;
                            enemies.splice(j, 1);
                        }
                        break;
                    }
                }
            }

            // Update Enemies
            enemies.forEach(en => {
                en.x += en.vx;
                // Simple patrol bounds
                if (en.x < cameraX - 100 || en.x > cameraX + 900) {
                    en.vx *= -1;
                }

                // Check player collision with enemy
                if (
                    player.x < en.x + en.width &&
                    player.x + player.width > en.x &&
                    player.y < en.y + en.height &&
                    player.y + player.height > en.y
                ) {
                    hp--;
                    player.x -= 40; // knockback
                    if (hp <= 0) {
                        alert("Mission Failed! Game Over.");
                        hp = 3;
                        score = 0;
                        player.x = 100;
                        cameraX = 0;
                    }
                }
            });

            // Stage progression / spawning forward enemies
            if (enemies.length < 4 && Math.random() < 0.02) {
                let spawnX = cameraX + 800 + Math.random() * 200;
                enemies.push({
                    x: spawnX,
                    y: 330,
                    width: 40,
                    height: 50,
                    vx: -(1 + Math.random() * 2),
                    hp: 2,
                    type: "mercenary"
                });
            }

            // Update UI
            document.getElementById("stageDisplay").innerText = `${stage} - ${stageName}`;
            document.getElementById("scoreDisplay").innerText = score;
            document.getElementById("hpDisplay").innerText = "♥".repeat(Math.max(0, hp));
        }

        function drawRetroMonkey(x, y, facing) {
            ctx.save();
            // Pixelated Retro Styling
            ctx.translate(x, y);
            if (facing < 0) {
                ctx.scale(-1, 1);
                ctx.translate(-44, 0);
            }

            // Body (Brown Fur)
            ctx.fillStyle = "#8B4513";
            ctx.fillRect(8, 20, 28, 26);

            // Head & Tan Face
            ctx.fillStyle = "#A0522D";
            ctx.fillRect(10, 4, 26, 20);
            ctx.fillStyle = "#DEB887";
            ctx.fillRect(16, 10, 18, 12);

            // Eyes & Expression
            ctx.fillStyle = "#000";
            ctx.fillRect(19, 13, 3, 4);
            ctx.fillRect(28, 13, 3, 4);

            // Retro Red Headband / Military Bandana
            ctx.fillStyle = "#CC0000";
            ctx.fillRect(8, 4, 30, 5);
            ctx.fillRect(34, 6, 8, 3); // Bandana tail trailing

            // Boxer Shorts / Belt
            ctx.fillStyle = "#FFD700";
            ctx.fillRect(8, 42, 28, 6);

            // Big Retro Pixel Boxer Gloves
            ctx.fillStyle = "#FF0000";
            if (keys["j"] || keys[" "]) {
                // Punching extension
                ctx.fillRect(34, 22, 16, 14);
            } else {
                ctx.fillRect(28, 26, 14, 14);
            }

            // Legs / Boots
            ctx.fillStyle = "#333";
            ctx.fillRect(10, 48, 8, 4);
            ctx.fillRect(26, 48, 8, 4);

            ctx.restore();
        }

        function drawEnemy(en) {
            ctx.save();
            ctx.translate(en.x, en.y);
            // Enemy Body (Green military uniform style)
            ctx.fillStyle = "#2E8B57";
            ctx.fillRect(5, 15, 30, 30);
            // Helmet
            ctx.fillStyle = "#556B2F";
            ctx.fillRect(2, 5, 36, 12);
            // Rifle
            ctx.fillStyle = "#111";
            ctx.fillRect(-8, 22, 16, 5);
            ctx.restore();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Parallax Background Scenery (Retro City Skyline)
            ctx.fillStyle = "#2c3e50";
            let bgOffset = (cameraX * 0.3) % 800;
            ctx.fillRect(-bgOffset, 150, 300, 200);
            ctx.fillRect(300 - bgOffset, 100, 250, 250);
            ctx.fillRect(600 - bgOffset, 180, 350, 170);
            ctx.fillRect(950 - bgOffset, 80, 300, 270);

            // Ground platform
            ctx.fillStyle = "#4a6572";
            ctx.fillRect(0, 350, canvas.height, 100);
            
            // Ground detail lines
            ctx.strokeStyle = "#34495e";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, 350);
            ctx.lineTo(800, 350);
            ctx.stroke();

            // Draw Enemies
            enemies.forEach(en => {
                if (en.x + en.width > cameraX && en.x < cameraX + 800) {
                    ctx.save();
                    ctx.translate(-cameraX, 0);
                    drawEnemy(en);
                    ctx.restore();
                }
            });

            // Draw Bullets (Bananas / Energy rounds)
            ctx.fillStyle = "#FFD700";
            bullets.forEach(b => {
                ctx.beginPath();
                ctx.arc(b.x - cameraX, b.y, b.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            // Draw Player
            ctx.save();
            ctx.translate(-cameraX, 0);
            drawRetroMonkey(player.x, player.y, player.facing);
            ctx.restore();
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        loop();
    </script>
</body>
</html>
"""

components.html(game_code, height=520, scrolling=False)
