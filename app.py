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
    <div id="controls-hint">Controls: A/D or Left/Right to Move | W or Up Arrow to Jump | Space or J to Shoot Bananas</div>
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
        let invincibilityTimer = 0;
        let messageTimer = 0;
        let overlayMessage = "";

        // Player (Retro Pixel Monkey)
        let player = {
            x: 100,
            y: 298, // Aligned with ground level (350 - 52 height)
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
        // Enemies correctly placed on the ground (groundLevel 350 - enemy height 50 = 300)
        let enemies = [
            { x: 600, y: 300, width: 40, height: 50, vx: -1.5, hp: 2, type: "mercenary" },
            { x: 950, y: 300, width: 40, height: 50, vx: -2, hp: 3, type: "mercenary" },
            { x: 1400, y: 290, width: 50, height: 60, vx: -1, hp: 5, type: "heavy" }
        ];

        window.addEventListener("keydown", (e) => { 
            // Prevent default scrolling behavior for game control keys
            if(["space", "arrowup", "arrowdown", "arrowleft", "arrowright"].includes(e.key.toLowerCase()) || e.key === " ") {
                e.preventDefault();
            }

            let key = e.key.toLowerCase();
            keys[key] = true; 

            // JUMP: Only W or Up Arrow
            if ((key === "w" || e.key === "ArrowUp") && player.grounded) {
                player.vy = player.jumpForce;
                player.grounded = false;
            }

            // SHOOT: Only Space or J
            if (key === "j" || e.key === " ") {
                shootBullet();
            }
        });

        window.addEventListener("keyup", (e) => { 
            keys[e.key.toLowerCase()] = false; 
        });

        function shootBullet() {
            bullets.push({
                x: player.facing > 0 ? player.x + player.width : player.x - 10,
                y: player.y + 24, // Aligned directly with monkey hand height
                vx: player.facing * 10,
                radius: 7
            });
        }

        function update() {
            if (invincibilityTimer > 0) invincibilityTimer--;
            if (messageTimer > 0) messageTimer--;

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
            if (player.x < cameraX + 50) player.x = cameraX + 50;

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

            // Update Bullets & Hitboxes
            for (let i = bullets.length - 1; i >= 0; i--) {
                bullets[i].x += bullets[i].vx;
                if (bullets[i].x > cameraX + 850 || bullets[i].x < cameraX - 50) {
                    bullets.splice(i, 1);
                    continue;
                }

                // Check collision with enemies (generous hitbox for easy hitting)
                for (let j = enemies.length - 1; j >= 0; j--) {
                    let en = enemies[j];
                    if (
                        bullets[i] &&
                        bullets[i].x > en.x - 5 && 
                        bullets[i].x < en.x + en.width + 5 &&
                        bullets[i].y > en.y - 5 && 
                        bullets[i].y < en.y + en.height + 5
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
                if (en.x < cameraX - 100 || en.x > cameraX + 900) {
                    en.vx *= -1;
                }

                // Check player collision with enemy
                if (
                    invincibilityTimer === 0 &&
                    player.x < en.x + en.width &&
                    player.x + player.width > en.x &&
                    player.y < en.y + en.height &&
                    player.y + player.height > en.y
                ) {
                    hp--;
                    invincibilityTimer = 60; // 1 second immunity
                    player.vy = -6;
                    player.x -= 30;
                    
                    if (hp <= 0) {
                        overlayMessage = "OOF! HEALTH DEPLETED - RESPAWNING...";
                        messageTimer = 120;
                        hp = 3;
                        player.x = cameraX + 100;
                    }
                }
            });

            // Stage progression / spawning forward enemies
            if (enemies.length < 4 && Math.random() < 0.02) {
                let spawnX = cameraX + 800 + Math.random() * 200;
                enemies.push({
                    x: spawnX,
                    y: 350 - 50, // accurately placed on ground
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
            if (invincibilityTimer > 0 && Math.floor(invincibilityTimer / 4) % 2 === 0) {
                return; // blinking effect
            }

            ctx.save();
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

            // Eyes
            ctx.fillStyle = "#000";
            ctx.fillRect(19, 13, 3, 4);
            ctx.fillRect(28, 13, 3, 4);

            // Retro Red Headband
            ctx.fillStyle = "#CC0000";
            ctx.fillRect(8, 4, 30, 5);
            ctx.fillRect(34, 6, 8, 3);

            // Boxer Belt
            ctx.fillStyle = "#FFD700";
            ctx.fillRect(8, 42, 28, 6);

            // Boxer Gloves (Extended when shooting Space or J)
            ctx.fillStyle = "#FF0000";
            if (keys["j"] || keys[" "]) {
                ctx.fillRect(34, 22, 16, 14);
            } else {
                ctx.fillRect(28, 26, 14, 14);
            }

            // Boots
            ctx.fillStyle = "#333";
            ctx.fillRect(10, 48, 8, 4);
            ctx.fillRect(26, 48, 8, 4);

            ctx.restore();
        }

        function drawEnemy(en) {
            ctx.save();
            ctx.translate(en.x, en.y);
            ctx.fillStyle = "#2E8B57";
            ctx.fillRect(5, 15, 30, 30);
            ctx.fillStyle = "#556B2F";
            ctx.fillRect(2, 5, 36, 12);
            ctx.fillStyle = "#111";
            ctx.fillRect(-8, 22, 16, 5);
            ctx.restore();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Parallax Background Scenery
            ctx.fillStyle = "#2c3e50";
            let bgOffset = (cameraX * 0.3) % 800;
            ctx.fillRect(-bgOffset, 150, 300, 200);
            ctx.fillRect(300 - bgOffset, 100, 250, 250);
            ctx.fillRect(600 - bgOffset, 180, 350, 170);
            ctx.fillRect(950 - bgOffset, 80, 300, 270);

            // Ground platform
            ctx.fillStyle = "#4a6572";
            ctx.fillRect(0, 350, canvas.width, 100);
            
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

            // Draw Bullets (Bananas)
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

            // Warning Message Overlay
            if (messageTimer > 0) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                ctx.fillRect(150, 180, 500, 70);
                ctx.strokeStyle = "#ff4444";
                ctx.lineWidth = 2;
                ctx.strokeRect(150, 180, 500, 70);
                
                ctx.fillStyle = "#ff5555";
                ctx.font = "bold 18px 'Courier New'";
                ctx.textAlign = "center";
                ctx.fillText(overlayMessage, 400, 222);
                ctx.textAlign = "left";
            }
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
