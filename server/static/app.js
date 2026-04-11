const promptEl = document.getElementById("prompt");
const rewardEl = document.getElementById("reward");
const levelEl = document.getElementById("level");
const roundEl = document.getElementById("round");
const livesEl = document.getElementById("lives");
const streakEl = document.getElementById("streak");
const statusEl = document.getElementById("status");
const feedbackEl = document.getElementById("feedback");
const totalScoreEl = document.getElementById("totalScore");
const averageScoreEl = document.getElementById("averageScore");
const correctCountEl = document.getElementById("correctCount");
const accuracyEl = document.getElementById("accuracy");
const bestScoreEl = document.getElementById("bestScore");
const bestRoundEl = document.getElementById("bestRound");
const resetBtn = document.getElementById("resetBtn");
const resetRoundBtn = document.getElementById("resetRoundBtn");
const healthBtn = document.getElementById("healthBtn");
const stepBtn = document.getElementById("stepBtn");
const explanationEl = document.getElementById("explanation");
const roundOverEl = document.getElementById("roundOver");
const roundOverBtn = document.getElementById("roundOverBtn");
const roundOverScoreEl = document.getElementById("roundOverScore");
const roundOverAccEl = document.getElementById("roundOverAcc");
const roundOverBestScoreEl = document.getElementById("roundOverBestScore");
const roundOverBestRoundEl = document.getElementById("roundOverBestRound");

let currentDecision = "safe";
let currentLevel = "easy";
let currentPrompt = null;
let totalRounds = 0; // 0 means infinite
let gameStarted = false;

function bestKey(level, key) {
  return `promptshield_${level}_${key}`;
}

function getBest(level) {
  return {
    score: parseFloat(localStorage.getItem(bestKey(level, "best_score")) || "0"),
    round: parseInt(localStorage.getItem(bestKey(level, "best_round")) || "0", 10),
  };
}

function setBest(level, score, round) {
  localStorage.setItem(bestKey(level, "best_score"), score.toFixed(1));
  localStorage.setItem(bestKey(level, "best_round"), String(round));
}

function setStatus(text) {
  statusEl.textContent = text;
}

function showRoundOver(obs) {
  if (!roundOverEl) return;
  const attempts = Math.max(1, obs.attempts ?? 1);
  const rawAcc = ((obs.correct_count ?? 0) / attempts) * 100;
  const acc = Math.min(100, Math.round(rawAcc));
  const level = obs.task_level || currentLevel;
  if (roundOverScoreEl) {
    roundOverScoreEl.textContent = (obs.total_score ?? 0).toFixed(1);
  }
  if (roundOverAccEl) {
    roundOverAccEl.textContent = `${acc}%`;
  }
  const best = getBest(level);
  if (roundOverBestScoreEl) roundOverBestScoreEl.textContent = best.score.toFixed(1);
  if (roundOverBestRoundEl) roundOverBestRoundEl.textContent = best.round;
  roundOverEl.classList.remove("hidden");
}

function hideRoundOver() {
  if (!roundOverEl) return;
  roundOverEl.classList.add("hidden");
}

function setActive(group, value) {
  group.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.value === value);
  });
}

function updateScoreboard(obs) {
  totalScoreEl.textContent = (obs.total_score ?? 0).toFixed(1);
  averageScoreEl.textContent = (obs.average_score ?? 0).toFixed(2);
  correctCountEl.textContent = obs.correct_count ?? 0;
  const attempts = Math.max(1, obs.attempts ?? 1);
  const rawAcc = ((obs.correct_count ?? 0) / attempts) * 100;
  const acc = Math.min(100, Math.round(rawAcc));
  accuracyEl.textContent = `${acc}%`;

  const level = obs.task_level || currentLevel;
  const best = getBest(level);
  const currentScore = obs.total_score ?? 0;
  const currentRound = obs.round_index ?? 0;
  if (currentScore > best.score) {
    setBest(level, currentScore, currentRound);
  } else if (currentRound > best.round) {
    setBest(level, best.score, currentRound);
  }
  const updated = getBest(level);
  if (bestScoreEl) bestScoreEl.textContent = updated.score.toFixed(1);
  if (bestRoundEl) bestRoundEl.textContent = updated.round;
}

function formatRounds(obs) {
  const total = obs.total_rounds ?? 0;
  if (total <= 0) {
    return `${obs.round_index}/∞`;
  }
  return `${obs.round_index}/${total}`;
}

const decisionButtons = Array.from(document.querySelectorAll(".toggle__btn")).map((btn) => {
  btn.dataset.value = btn.dataset.decision;
  btn.addEventListener("click", () => {
    currentDecision = btn.dataset.decision;
    setActive(decisionButtons, currentDecision);
  });
  return btn;
});
setActive(decisionButtons, currentDecision);

const levelButtons = Array.from(document.querySelectorAll(".segmented__btn")).map((btn) => {
  btn.dataset.value = btn.dataset.level;
  btn.addEventListener("click", () => {
    currentLevel = btn.dataset.level;
    levelEl.textContent = btn.dataset.level.charAt(0).toUpperCase() + btn.dataset.level.slice(1);
    setActive(levelButtons, currentLevel);
    if (gameStarted) {
      loadLevelState();
    }
  });
  return btn;
});
setActive(levelButtons, currentLevel);

async function checkHealth() {
  setStatus("Checking...");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    setStatus(data.status || "healthy");
  } catch (err) {
    setStatus("Offline");
  }
}

async function resetEnv() {
  setStatus("Resetting...");
  try {
    const res = await fetch("/game/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_level: currentLevel, total_rounds: totalRounds })
    });
    const obs = await res.json();
    currentPrompt = obs;
    hideRoundOver();
    promptEl.textContent = obs.prompt_text || "0";
    rewardEl.textContent = obs.reward ?? "0";
    if (feedbackEl) {
      feedbackEl.textContent = obs.feedback || "Awaiting your decision...";
    }
    levelEl.textContent = obs.task_level ? obs.task_level.charAt(0).toUpperCase() + obs.task_level.slice(1) : "Easy";
    roundEl.textContent = formatRounds(obs);
    if ((obs.task_level || currentLevel) === "easy" && obs.lives > 1000) {
      livesEl.textContent = "∞";
    } else {
      livesEl.textContent = obs.lives;
    }
    streakEl.textContent = obs.streak;
    updateScoreboard(obs);
    gameStarted = true;
    setStatus("Ready");
  } catch (err) {
    setStatus("Error");
  }
}

async function loadLevelState() {
  setStatus("Loading...");
  try {
    const res = await fetch("/game/state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_level: currentLevel, total_rounds: totalRounds })
    });
    const obs = await res.json();
    currentPrompt = obs;
    promptEl.textContent = obs.prompt_text || "0";
    rewardEl.textContent = obs.reward ?? "0";
    if (feedbackEl) {
      feedbackEl.textContent = obs.feedback || "Awaiting your decision...";
    }
    levelEl.textContent = obs.task_level ? obs.task_level.charAt(0).toUpperCase() + obs.task_level.slice(1) : "Easy";
    roundEl.textContent = formatRounds(obs);
    if ((obs.task_level || currentLevel) === "easy" && obs.lives > 1000) {
      livesEl.textContent = "∞";
    } else {
      livesEl.textContent = obs.lives;
    }
    streakEl.textContent = obs.streak;
    updateScoreboard(obs);
    gameStarted = true;
    setStatus("Ready");
  } catch (err) {
    setStatus("Error");
  }
}

async function stepEnv() {
  if (!currentPrompt) {
    setStatus("Reset first");
    return;
  }
  setStatus("Scoring...");
  try {
    const res = await fetch("/game/step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task_level: currentLevel,
        decision: currentDecision,
        explanation: explanationEl.value || null,
      })
    });
    const obs = await res.json();
    rewardEl.textContent = obs.reward ?? "0";
    promptEl.textContent = obs.prompt_text || "0";
    if (feedbackEl) {
      feedbackEl.textContent = obs.feedback || "No feedback available.";
    }
    roundEl.textContent = formatRounds(obs);
    if ((obs.task_level || currentLevel) === "easy" && obs.lives > 1000) {
      livesEl.textContent = "∞";
    } else {
      livesEl.textContent = obs.lives;
    }
    streakEl.textContent = obs.streak;
    updateScoreboard(obs);
    explanationEl.value = "";
    if (obs.done && obs.lives === 0) {
      setStatus("Round over");
      showRoundOver(obs);
      return;
    }
    setStatus(obs.done ? "Round complete" : "Next prompt");
  } catch (err) {
    setStatus("Error");
  }
}

resetBtn.addEventListener("click", resetEnv);
if (resetRoundBtn) {
  resetRoundBtn.addEventListener("click", resetEnv);
}
if (roundOverBtn) {
  roundOverBtn.addEventListener("click", resetEnv);
}
healthBtn.addEventListener("click", checkHealth);
stepBtn.addEventListener("click", stepEnv);
