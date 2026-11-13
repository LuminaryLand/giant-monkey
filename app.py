<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monkey Slug: Jungle Warfare</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background-color: #0b0f19;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            overflow: hidden;
        }
        #game-container {
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            border: 4px solid #374151;
            border-radius: 12px;
            overflow: hidden;
            background: #1f2937;
        }
        canvas {
            display: block;
            background: linear-gradient(to bottom, #1e3a8a, #93c5fd);
        }
        .ui-overlay {
            position: absolute;
            top: 15px;
            left: 15px;
            right: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
            font-size: 18px;
            letter-spacing: 1px;
        }
        .stat-badge {
            background: rgba(15, 23, 42, 0.7);
            padding: 8px 16px;
            border-radius: 8px;
            border: 2px solid #60a5fa;
            display: flex;
            gap: 10px;
        }
        .controls-hint {
            margin-top: 15px;
            text-align: center;
            color: #9ca3af;
            font-size: 13px;
            background: rgba(31, 41, 55, 0.8);
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #4b5563;
        }
        kbd {
            background: #374151;
            color: #fff;
            padding: 2px 6px;
            border-radius: 4px;
            border-bottom: 2px solid #1f2937;
            font-family: monospace;
        }
    </style>
</head>
<body>

<div id="game-container">
    <div class="ui-overlay">
        <div class="stat-badge">
            <span>❤️ HP: <span id="hpDisplay">100</span></span>
            <span>🍌 BANANAS: <span id="scoreDisplay">0</span></span>
        </div>
        <div class="stat-badge">
            <span>🎯 STAGE: <span id="stageDisplay">1 - Jungle Ruins</span></span>
        </div>
    </div>
    <canvas id="gameCanvas" width="800" height="450"></canvas>
</div>

<div class="controls-hint">
    Controls: <kbd>A</kbd> / <kbd>D</kbd> or <kbd>←</kbd> / <kbd>→</kbd> Move | <kbd>W</kbd> or <kbd>↑</kbd> Jump | <kbd>Space</kbd> Shoot Banana Blaster!
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Game States
let gameState = "START"; // START, PLAYING, GAMEOVER, VICTORY
let score = 0;
let stage = 1;
let cameraX = 0;

// Player (Boxer Monkey)
let player = {
    x: 100,
    y: 300,
    width: 48,
    height: 56,
    vx: 0,
    vy: 0,
    speed: 4,
    jumpPower: -11,
    gravity: 0.5,
    grounded: false,
    facing: 1, // 1 for right, -1 for left
    hp: 100,
    maxHp: 100,
    isShooting: false,
    shootTimer: 0
};

// Input State
let keys = {};

window.addEventListener("keydown", e => {
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " "].includes(e.key)) {
        e.preventDefault();
    }
    keys[e.key] = true;
    
    if (gameState === "START" || gameState === "GAMEOVER" || gameState === "VICTORY") {
        if (e.key === " " || e.key === "Enter") {
            resetGame();
            gameState = "PLAYING";
        }
    }
});

window.addEventListener("keyup", e => {
    keys[e.key] = false;
});

// Entities
let bullets = [];
let enemyBullets = [];
let enemies = [];
let platforms = [];
let items = [];
let boss = null;

function resetGame() {
    score = 0;
    stage = 1;
    cameraX = 0;
    player.hp = 100;
    player.x = 100;
    player.y = 250;
    player.vx = 0;
    player.vy = 0;
    loadStage(stage);
}

function loadStage(stg) {
    bullets = [];
    enemyBullets = [];
    items = [];
    boss = null;
    
    if (stg === 1) {
        platforms = [
            { x: 0, y: 380, w: 2400, h: 70, type: "ground" },
            { x: 350, y: 280, w: 180, h: 20, type: "plat" },
            { x: 650, y: 210, w: 200, h: 20, type: "plat" },
            { x: 980, y: 270, w: 220, h: 20, type: "plat" },
            { x: 1350, y: 200, w: 180, h: 20, type: "plat" },
            { x: 1700, y: 280, w: 250, h: 20, type: "plat" }
        ];
        
        enemies = [
            { x: 400, y: 330, w: 40, h: 50, vx: -1.5, patrolMin: 350, patrolMax: 550, hp: 30, type: "grunt", shootCd: 100, timer: 0 },
            { x: 750, y: 160, w: 40, h: 50, vx: 0, patrolMin: 650, patrolMax: 850, hp: 40, type: "sniper", shootCd: 80, timer: 0 },
            { x: 1050, y: 220, w: 40, h: 50, vx: 1, patrolMin: 980, patrolMax: 1200, hp: 30, type: "grunt", shootCd: 90, timer: 0 },
            { x: 1400, y: 150, w: 40, h: 50, vx: 0, patrolMin: 1350, patrolMax: 1530, hp: 50, type: "sniper", shootCd: 70, timer: 0 },
            { x: 1800, y: 330, w: 40, h: 50, vx: -2, patrolMin: 1700, patrolMax: 1950, hp: 40, type: "grunt", shootCd: 60, timer: 0 }
        ];
        
        // Stage Boss
        boss = {
            x: 2100,
            y: 280,
            w: 80,
            h: 90,
            vx: -1,
            hp: 250,
            maxHp: 250,
            shootCd: 50,
            timer: 0,
            active: false
        };
    }
}

function update() {
    if (gameState !== "PLAYING") return;

    // Player horizontal movement
    player.vx = 0;
    if (keys["ArrowLeft"] || keys["a"] || keys["A"]) {
        player.vx = -player.speed;
        player.facing = -1;
    }
    if (keys["ArrowRight"] || keys["d"] || keys["D"]) {
        player.vx = player.speed;
        player.facing = 1;
    }

    // Player jump
    if ((keys["ArrowUp"] || keys["w"] || keys["W"]) && player.grounded) {
        player.vy = player.jumpPower;
        player.grounded = false;
    }

    // Gravity
    player.vy += player.gravity;

    // Apply Velocity
    player.x += player.vx;
    player.y += player.vy;

    // Camera follow player smoothly
    let targetCameraX = player.x - 250;
    if (targetCameraX < 0) targetCameraX = 0;
    if (targetCameraX > 1600) targetCameraX = 1600;
    cameraX += (targetCameraX - cameraX) * 0.1;

    // Platform collisions
    player.grounded = false;
    platforms.forEach(p => {
        if (
            player.x + player.width > p.x &&
            player.x < p.x + p.w &&
            player.y + player.height >= p.y &&
            player.y + player.height <= p.y + p.h + 12 &&
            player.vy >= 0
        ) {
            player.y = p.y - player.height;
            player.vy = 0;
            player.grounded = true;
        }
    });

    // Boundaries
    if (player.x < 0) player.x = 0;
    if (player.x > 2350) player.x = 2350;
    if (player.y > 500) {
        player.hp = 0;
        gameState = "GAMEOVER";
    }

    // Shooting mechanics
    if (player.shootTimer > 0) player.shootTimer--;
    if ((keys[" "] ) && player.shootTimer === 0) {
        bullets.push({
            x: player.facing === 1 ? player.x + player.width : player.x - 16,
            y: player.y + 20,
            vx: player.facing * 10,
            width: 16,
            height: 8
        });
        player.shootTimer = 12; // Fire rate limit
    }

    // Update Player Bullets
    bullets.forEach((b, index) => {
        b.x += b.vx;
        // Check collision with enemies
        enemies.forEach(e => {
            if (
                b.x < e.x + e.w &&
                b.x + b.width > e.x &&
                b.y < e.y + e.h &&
                b.y + b.height > e.y
            ) {
                e.hp -= 15;
                bullets.splice(index, 1);
            }
        });

        // Check collision with boss
        if (boss && boss.active) {
            if (
                b.x < boss.x + boss.w &&
                b.x + b.width > boss.x &&
                b.y < boss.y + boss.h &&
                b.y + b.height > boss.y
            ) {
                boss.hp -= 15;
                bullets.splice(index, 1);
                if (boss.hp <= 0) {
                    score += 500;
                    gameState = "VICTORY";
                }
            }
        }
    });

    // Remove offscreen bullets
    bullets = bullets.filter(b => b.x > cameraX && b.x < cameraX + 900);

    // Update Enemies
    enemies.forEach(e => {
        e.x += e.vx;
        if (e.x < e.patrolMin || e.x > e.patrolMax) e.vx *= -1;

        // Enemy shooting
        e.timer++;
        if (e.timer >= e.shootCd) {
            e.timer = 0;
            let dir = player.x < e.x ? -1 : 1;
            enemyBullets.push({
                x: e.x,
                y: e.y + 20,
                vx: dir * 5,
                width: 10,
                height: 6
            });
        }

        // Check player collision with enemy body
        if (
            player.x < e.x + e.w &&
            player.x + player.width > e.x &&
            player.y < e.y + e.h &&
            player.y + player.height > e.y
        ) {
            player.hp -= 1;
            if (player.hp <= 0) gameState = "GAMEOVER";
        }
    });

    // Filter dead enemies & add score/items
    enemies = enemies.filter(e => {
        if (e.hp <= 0) {
            score += 100;
            items.push({ x: e.x + 10, y: e.y + 20, type: "banana" });
            return false;
        }
        return true;
    });

    // Boss Activation & Logic
    if (player.x > 1850 && boss && !boss.active) {
        boss.active = true;
    }

    if (boss && boss.active) {
        boss.x += boss.vx;
        if (boss.x < 1950 || boss.x > 2250) boss.vx *= -1;
        boss.timer++;
        if (boss.timer >= boss.shootCd) {
            boss.timer = 0;
            enemyBullets.push({ x: boss.x, y: boss.y + 40, vx: -6, width: 14, height: 8 });
            enemyBullets.push({ x: boss.x, y: boss.y + 40, vx: -3, vy: -1, width: 14, height: 8 });
        }

        // Boss touch damage
        if (
            player.x < boss.x + boss.w &&
            player.x + player.width > boss.x &&
            player.y < boss.y + boss.h &&
            player.y + player.height > boss.y
        ) {
            player.hp -= 2;
            if (player.hp <= 0) gameState = "GAMEOVER";
        }
    }

    // Update Enemy Bullets
    enemyBullets.forEach((eb, index) => {
        eb.x += eb.vx;
        if (eb.vy) eb.vy += 0.2; // optional arc
        
        // Check player hit
        if (
            eb.x < player.x + player.width &&
            eb.x + eb.width > player.x &&
            eb.y < player.y + player.height &&
            eb.y + eb.height > player.y
        ) {
            player.hp -= 12;
            enemyBullets.splice(index, 1);
            if (player.hp <= 0) gameState = "GAMEOVER";
        }
    });
    enemyBullets = enemyBullets.filter(eb => eb.x > cameraX - 50 && eb.x < cameraX + 850);

    // Collectibles
    items.forEach((item, index) => {
        if (
            player.x < item.x + 25 &&
            player.x + player.width > item.x &&
            player.y < item.y + 25 &&
            player.y + player.height > item.y
        ) {
            score += 50;
            player.hp = Math.min(player.maxHp, player.hp + 15);
            items.splice(index, 1);
        }
    });

    // Update UI elements
    document.getElementById("hpDisplay").innerText = Math.max(0, player.hp);
    document.getElementById("scoreDisplay").innerText = score;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(-cameraX, 0);

    // Background Scenery / Parallax Jungle Trees
    ctx.fillStyle = "#1e293b";
    for (let i = 0; i < 10; i++) {
        ctx.fillRect(i * 300 - (cameraX * 0.3), 150, 60, 230);
        ctx.fillStyle = "#15803d";
        ctx.beginPath();
        ctx.arc(i * 300 + 30 - (cameraX * 0.3), 150, 70, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#1e293b";
    }

    // Draw Platforms / Ground
    platforms.forEach(p => {
        if (p.type === "ground") {
            ctx.fillStyle = "#166534";
            ctx.fillRect(p.x, p.y, p.w, p.h);
            ctx.fillStyle = "#14532d";
            ctx.fillRect(p.x, p.y, p.w, 12); // Grass top
        } else {
            ctx.fillStyle = "#9a3412";
            ctx.fillRect(p.x, p.y, p.w, p.h);
            ctx.strokeStyle = "#c2410c";
            ctx.lineWidth = 3;
            ctx.strokeRect(p.x, p.y, p.w, p.h);
        }
    });

    // Draw Items (Bananas)
    items.forEach(item => {
        ctx.fillStyle = "#facc15";
        ctx.beginPath();
        ctx.arc(item.x + 10, item.y + 10, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#ca8a04";
        ctx.font = "12px sans-serif";
        ctx.fillText("🍌", item.x, item.y + 15);
    });

    // Draw Player (Boxer Monkey)
    ctx.fillStyle = "#92400e"; // Fur
    ctx.fillRect(player.x, player.y, player.width, player.height);
    
    // Head & Boxer Headgear
    ctx.fillStyle = "#78350f";
    ctx.fillRect(player.x + (player.facing === 1 ? 24 : -4), player.y - 14, 28, 26);
    ctx.fillStyle = "#dc2626"; // Red Red Headband/Cap
    ctx.fillRect(player.x + (player.facing === 1 ? 22 : -6), player.y - 18, 32, 10);

    // Boxer Gloves
    ctx.fillStyle = "#ef4444";
    let gloveX = player.facing === 1 ? player.x + player.width - 4 : player.x - 16;
    ctx.fillRect(gloveX, player.y + 24, 22, 22);

    // Draw Bullets
    ctx.fillStyle = "#fde047";
    bullets.forEach(b => {
        ctx.fillRect(b.x, b.y, b.width, b.height);
    });

    // Draw Enemy Bullets
    ctx.fillStyle = "#f97316";
    enemyBullets.forEach(eb => {
        ctx.fillRect(eb.x, eb.y, eb.width, eb.height);
    });

    // Draw Enemies
    enemies.forEach(e => {
        ctx.fillStyle = e.type === "sniper" ? "#475569" : "#334155";
        ctx.fillRect(e.x, e.y, e.w, e.h);
        // Enemy Helmet / Visor
        ctx.fillStyle = "#64748b";
        ctx.fillRect(e.x + 5, e.y + 5, e.w - 10, 14);
        
        // Enemy Health Bar
        ctx.fillStyle = "#991b1b";
        ctx.fillRect(e.x, e.y - 10, e.w, 5);
        ctx.fillStyle = "#22c55e";
        ctx.fillRect(e.x, e.y - 10, (e.hp / 40) * e.w, 5);
    });

    // Draw Boss
    if (boss) {
        ctx.fillStyle = boss.active ? "#7f1d1d" : "#451a03";
        ctx.fillRect(boss.x, boss.y, boss.w, boss.h);
        // Boss Cannon
        ctx.fillStyle = "#0f172a";
        ctx.fillRect(boss.x - 20, boss.y + 30, 25, 14);

        if (boss.active) {
            // Boss Health Bar Header
            ctx.fillStyle = "#7f1d1d";
            ctx.fillRect(boss.x - 20, boss.y - 16, boss.w + 40, 8);
            ctx.fillStyle = "#ef4444";
            ctx.fillRect(boss.x - 20, boss.y - 16, ((boss.hp / boss.maxHp) * (boss.w + 40)), 8);
        }
    }

    ctx.restore();

    // Start / Game Over / Victory Overlays rendered in screen space
    if (gameState !== "PLAYING") {
        ctx.fillStyle = "rgba(11, 15, 25, 0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.textAlign = "center";
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 32px sans-serif";
        
        if (gameState === "START") {
            ctx.fillText("🦍 MONKEY SLUG: JUNGLE WARFARE", canvas.width / 2, 160);
            ctx.fillStyle = "#60a5fa";
            ctx.font = "18px sans-serif";
            ctx.fillText("Press [SPACEBAR] or [ENTER] to Start Mission", canvas.width / 2, 230);
        } else if (gameState === "GAMEOVER") {
            ctx.fillStyle = "#ef4444";
            ctx.fillText("MISSION FAILED", canvas.width / 2, 170);
            ctx.fillStyle = "#ffffff";
            ctx.font = "20px sans-serif";
            ctx.fillText(`Final Score: ${score}`, canvas.width / 2, 220);
            ctx.fillStyle = "#60a5fa";
            ctx.fillText("Press [SPACEBAR] to Retry", canvas.width / 2, 270);
        } else if (gameState === "VICTORY") {
            ctx.fillStyle = "#22c55e";
            ctx.fillText("STAGE CLEAR! VICTORY!", canvas.width / 2, 170);
            ctx.fillStyle = "#ffffff";
            ctx.font = "20px sans-serif";
            ctx.fillText(`Total Score: ${score}`, canvas.width / 2, 220);
            ctx.fillStyle = "#60a5fa";
            ctx.fillText("Press [SPACEBAR] to Play Again", canvas.width / 2, 270);
        }
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

// Initialize loop
gameLoop();
</script>

</body>
</html>
