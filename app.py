import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Giant Monkey: World Tour", page_icon="🦍", layout="wide")

st.title("🦍 Giant Monkey: World Tour")

# HTML/JS Game Component
game_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #111; color: white; font-family: sans-serif; text-align: center; }
        canvas { background: #222; display: block; margin: 0 auto; border: 2px solid #444; }
        #ui { margin-top: 10px; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <div id="ui">Level: <span id="levelDisplay">1 (City)</span> | Distance: <span id="distDisplay">0</span> / 1000m</div>
    <canvas id="gameCanvas" width="800" height="400"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Game State
        let level = 1;
        let distance = 0;
        let levelLength = 1000;
        let environmentName = "City";

        let player = {
            x: 100,
            y: 280,
            width: 50,
            height: 70,
            speed: 3,       // Continuous forward scroll speed
            isWalking: true // Always walking until level completes
        };

        let keys = {};

        window.addEventListener("keydown", (e) => { keys[e.key] = true; });
        window.addEventListener("keyup", (e) => { keys[e.key] = false; });

        function update() {
            // Continuous forward movement
            if (player.isWalking) {
                distance += 1; // Increment progress
            }

            // Steering / Up & Down or jump controls
            if (keys["ArrowUp"] || keys["w"]) player.y -= 4;
            if (keys["ArrowDown"] || keys["s"]) player.y += 4;
            
            // Keep player within vertical bounds
            if (player.y < 50) player.y = 50;
            if (player.y > 310) player.y = 310;

            // Check Level Completion
            if (distance >= levelLength) {
                level++;
                distance = 0;
                levelLength += 500; // Increase next level length
                if (level === 2) environmentName = "Small Town";
                else if (level === 3) environmentName = "Country";
                else environmentName = "World Tour Loop";
            }

            // Update UI elements
            document.getElementById("levelDisplay").innerText = `${level} (${environmentName})`;
            document.getElementById("distDisplay").innerText = distance;
        }

        function draw() {
            // Clear screen
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Background environment based on level
            ctx.fillStyle = level === 1 ? "#333" : (level === 2 ? "#423" : "#242");
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw Ground line
            ctx.strokeStyle = "#555";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, 350);
            ctx.lineTo(800, 350);
            ctx.stroke();

            // Draw Player (Boxer Monkey placeholder)
            ctx.fillStyle = "#8B4513"; // Brown fur
            ctx.fillRect(player.x, player.y, player.width, player.height);

            // Draw Boxer Gloves
            ctx.fillStyle = "#FF0000"; // Red gloves
            ctx.fillRect(player.x + 35, player.y + 30, 20, 20);

            // Draw moving ground markers/scenery simulation
            ctx.fillStyle = "#666";
            let offset = (distance * 5) % 800;
            for(let i = -1; i < 3; i++) {
                ctx.fillRect((i * 300) - (offset % 300), 340, 40, 10);
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

components.html(game_code, height=500)
