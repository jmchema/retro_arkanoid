const bootstrap = window.ARKANOID_BOOTSTRAP;

if (!bootstrap || !bootstrap.authenticated) {
    // The login screen has no game canvas.
} else {
    const messages = bootstrap.translations || {};
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    const overlay = document.getElementById("overlay");
    const overlayTitle = document.getElementById("overlayTitle");
    const overlayMessage = document.getElementById("overlayMessage");
    const restartButton = document.getElementById("restartButton");
    const scoreElement = document.getElementById("score");
    const livesElement = document.getElementById("lives");
    const overlayKicker = overlay.querySelector(".overlay-kicker");
    const maxScoreElement = document.getElementById("maxScore");
    const savedRunsCountElement = document.getElementById("savedRunsCount");
    const historyList = document.getElementById("historyList");

    const state = {
        running: false,
        started: false,
        won: false,
        score: 0,
        lives: 3,
        scoreSaved: false,
        isAnonymousGuest: Boolean(bootstrap.isAnonymousGuest),
        canSaveScores: Boolean(bootstrap.canSaveScores),
        maxScore: bootstrap.maxScore || 0,
        totalGamesCount: bootstrap.totalGamesCount || 0,
        keys: {
            left: false,
            right: false,
        },
    };

    const paddle = {
        width: 140,
        height: 16,
        speed: 9,
        x: (canvas.width - 140) / 2,
        y: canvas.height - 48,
    };

    const ball = {
        radius: 10,
        speed: 5.2,
        x: canvas.width / 2,
        y: canvas.height - 70,
        dx: 4.1,
        dy: -5.2,
    };

    const brickConfig = {
        rows: 6,
        cols: 10,
        width: 74,
        height: 24,
        gap: 10,
        topOffset: 86,
    };

    let bricks = [];

    function formatText(key, replacements = {}) {
        let text = messages[key] || key;
        Object.entries(replacements).forEach(([name, value]) => {
            text = text.replace(`{${name}}`, String(value));
        });
        return text;
    }

    function buildBricks() {
        const palette = ["#ff6b6b", "#ffd93d", "#6bff95", "#6ef2ff", "#a991ff", "#ff7be5"];
        const totalWidth =
            brickConfig.cols * brickConfig.width + (brickConfig.cols - 1) * brickConfig.gap;
        const leftOffset = (canvas.width - totalWidth) / 2;

        bricks = [];
        for (let row = 0; row < brickConfig.rows; row += 1) {
            for (let col = 0; col < brickConfig.cols; col += 1) {
                bricks.push({
                    x: leftOffset + col * (brickConfig.width + brickConfig.gap),
                    y: brickConfig.topOffset + row * (brickConfig.height + brickConfig.gap),
                    width: brickConfig.width,
                    height: brickConfig.height,
                    color: palette[row % palette.length],
                    alive: true,
                });
            }
        }
    }

    function resetBallAndPaddle() {
        paddle.x = (canvas.width - paddle.width) / 2;
        ball.x = canvas.width / 2;
        ball.y = canvas.height - 70;
        ball.dx = (Math.random() > 0.5 ? 1 : -1) * 4.1;
        ball.dy = -Math.abs(ball.speed);
    }

    function updateHud() {
        scoreElement.textContent = String(state.score);
        livesElement.textContent = String(state.lives);
        if (state.canSaveScores) {
            maxScoreElement.textContent = String(state.maxScore);
            savedRunsCountElement.textContent = String(state.totalGamesCount);
        }
    }

    function showOverlay(title, message, kicker = formatText("pause")) {
        overlayTitle.textContent = title;
        overlayMessage.textContent = message;
        overlayKicker.textContent = kicker;
        restartButton.textContent = state.started ? formatText("play_again") : formatText("start_game");
        overlay.classList.remove("hidden");
    }

    function hideOverlay() {
        overlay.classList.add("hidden");
    }

    function drawBackground() {
        const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
        gradient.addColorStop(0, "#091322");
        gradient.addColorStop(1, "#10263f");
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.strokeStyle = "rgba(255,255,255,0.05)";
        for (let x = 0; x < canvas.width; x += 32) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
    }

    function drawPaddle() {
        ctx.fillStyle = "#ffe066";
        ctx.shadowColor = "rgba(255, 224, 102, 0.6)";
        ctx.shadowBlur = 16;
        ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
        ctx.shadowBlur = 0;
    }

    function drawBall() {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = "#ff4db8";
        ctx.shadowColor = "rgba(255, 77, 184, 0.8)";
        ctx.shadowBlur = 20;
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.closePath();
    }

    function drawBricks() {
        bricks.forEach((brick) => {
            if (!brick.alive) {
                return;
            }

            ctx.fillStyle = brick.color;
            ctx.shadowColor = `${brick.color}88`;
            ctx.shadowBlur = 12;
            ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
            ctx.shadowBlur = 0;
        });
    }

    function drawCenterMessage() {
        if (state.running) {
            return;
        }

        ctx.fillStyle = "rgba(255,255,255,0.16)";
        ctx.font = "bold 16px Consolas";
        ctx.textAlign = "center";
        ctx.fillText(formatText("space_to_launch"), canvas.width / 2, canvas.height - 110);
    }

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawBackground();
        drawBricks();
        drawPaddle();
        drawBall();
        drawCenterMessage();
    }

    function movePaddle() {
        if (state.keys.left) {
            paddle.x -= paddle.speed;
        }
        if (state.keys.right) {
            paddle.x += paddle.speed;
        }

        if (paddle.x < 0) {
            paddle.x = 0;
        }
        if (paddle.x + paddle.width > canvas.width) {
            paddle.x = canvas.width - paddle.width;
        }
    }

    function bounceFromWalls() {
        if (ball.x + ball.dx > canvas.width - ball.radius || ball.x + ball.dx < ball.radius) {
            ball.dx *= -1;
        }

        if (ball.y + ball.dy < ball.radius) {
            ball.dy *= -1;
        }
    }

    function bounceFromPaddle() {
        const withinPaddleX = ball.x > paddle.x && ball.x < paddle.x + paddle.width;
        const touchingPaddle =
            ball.y + ball.radius >= paddle.y && ball.y + ball.radius <= paddle.y + paddle.height;

        if (withinPaddleX && touchingPaddle && ball.dy > 0) {
            const hitRatio = (ball.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2);
            ball.dx = hitRatio * 6.2;
            ball.dy = -Math.max(4.6, Math.abs(ball.dy));
            ball.y = paddle.y - ball.radius - 1;
        }
    }

    function hitBrick(brick) {
        const closestX = Math.max(brick.x, Math.min(ball.x, brick.x + brick.width));
        const closestY = Math.max(brick.y, Math.min(ball.y, brick.y + brick.height));
        const distanceX = ball.x - closestX;
        const distanceY = ball.y - closestY;

        if (distanceX * distanceX + distanceY * distanceY <= ball.radius * ball.radius) {
            brick.alive = false;
            state.score += 100;
            updateHud();

            if (Math.abs(distanceX) > Math.abs(distanceY)) {
                ball.dx *= -1;
            } else {
                ball.dy *= -1;
            }
        }
    }

    async function persistScore(won) {
        if (state.scoreSaved || !state.canSaveScores) {
            return;
        }

        state.scoreSaved = true;
        try {
            const response = await fetch(bootstrap.saveGameUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    score: state.score,
                    won,
                }),
            });

            if (!response.ok) {
                throw new Error("save_failed");
            }

            const payload = await response.json();
            if (payload.error) {
                return;
            }
            state.maxScore = payload.max_score;
            state.totalGamesCount = payload.total_games_count;
            updateHud();
            prependHistoryItem(payload);
        } catch (error) {
            console.error(formatText("save_game_error"), error);
        }
    }

    function prependHistoryItem(payload) {
        const empty = historyList.querySelector(".history-empty");
        if (empty) {
            empty.remove();
        }

        const item = document.createElement("li");
        const outcome = payload.won ? formatText("victory") : formatText("defeat");
        item.innerHTML = `<span>${payload.created_at}</span><strong>${payload.score}</strong><em>${outcome}</em>`;
        historyList.prepend(item);

        const items = historyList.querySelectorAll("li:not(.history-empty)");
        if (items.length > 5) {
            items[items.length - 1].remove();
        }
    }

    function handleWin() {
        state.running = false;
        state.won = true;
        const message = state.isAnonymousGuest
            ? formatText("win_message_guest", { score: state.score })
            : formatText("win_message", { score: state.score });
        showOverlay(formatText("you_win"), message, formatText("victory"));
        persistScore(true);
    }

    function handleBrickCollisions() {
        bricks.forEach((brick) => {
            if (brick.alive) {
                hitBrick(brick);
            }
        });

        if (bricks.every((brick) => !brick.alive)) {
            handleWin();
        }
    }

    function loseLife() {
        state.lives -= 1;
        updateHud();

        if (state.lives <= 0) {
            state.running = false;
            const message = state.isAnonymousGuest
                ? formatText("game_over_message_guest", { score: state.score })
                : formatText("game_over_message", { score: state.score });
            showOverlay(formatText("game_over"), message, formatText("defeat"));
            persistScore(false);
            return;
        }

        state.running = false;
        resetBallAndPaddle();
        showOverlay(
            formatText("ball_lost"),
            formatText("ball_lost_message", { lives: state.lives }),
            formatText("retry")
        );
    }

    function updateBall() {
        bounceFromWalls();
        bounceFromPaddle();
        handleBrickCollisions();

        ball.x += ball.dx;
        ball.y += ball.dy;

        if (ball.y - ball.radius > canvas.height) {
            loseLife();
        }
    }

    function startGame() {
        if (state.running || state.won || state.lives <= 0) {
            return;
        }

        state.running = true;
        state.started = true;
        hideOverlay();
    }

    function resetGame() {
        state.running = false;
        state.started = false;
        state.won = false;
        state.score = 0;
        state.lives = 3;
        state.scoreSaved = false;
        buildBricks();
        resetBallAndPaddle();
        updateHud();
        showOverlay(formatText("start_prompt"), formatText("move_prompt"), formatText("ready"));
        draw();
    }

    function gameLoop() {
        movePaddle();
        if (state.running) {
            updateBall();
        }
        draw();
        window.requestAnimationFrame(gameLoop);
    }

    function onKeyDown(event) {
        const key = event.key.toLowerCase();
        if (key === "arrowleft" || key === "a") {
            state.keys.left = true;
        }
        if (key === "arrowright" || key === "d") {
            state.keys.right = true;
        }
        if (key === " " || event.code === "Space") {
            event.preventDefault();
            startGame();
        }
        if (key === "r") {
            resetGame();
        }
    }

    function onKeyUp(event) {
        const key = event.key.toLowerCase();
        if (key === "arrowleft" || key === "a") {
            state.keys.left = false;
        }
        if (key === "arrowright" || key === "d") {
            state.keys.right = false;
        }
    }

    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("keyup", onKeyUp);
    restartButton.addEventListener("click", () => {
        resetGame();
        startGame();
    });

    window.addEventListener("blur", () => {
        state.keys.left = false;
        state.keys.right = false;
    });

    updateHud();
    resetGame();
    gameLoop();
}
