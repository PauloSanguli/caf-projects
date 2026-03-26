(function () {
  var root = document.getElementById("deadline-countdown");
  if (!root) return;
  var iso = root.dataset.deadline;
  if (!iso) return;
  var deadline = new Date(iso);
  if (isNaN(deadline.getTime())) return;

  var timerEl = root.querySelector("[data-countdown-timer]");
  if (!timerEl) return;

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function formatHMS(totalSeconds) {
    if (totalSeconds <= 0) return "00:00:00";
    var h = Math.floor(totalSeconds / 3600);
    var m = Math.floor((totalSeconds % 3600) / 60);
    var s = totalSeconds % 60;
    return pad(h) + ":" + pad(m) + ":" + pad(s);
  }

  var intervalId;

  function tick() {
    var diff = deadline - Date.now();
    var totalSeconds = Math.floor(diff / 1000);
    var text = formatHMS(totalSeconds);
    timerEl.textContent = text;
    timerEl.setAttribute("aria-label", "Tempo restante: " + text);
    if (totalSeconds <= 0) {
      if (intervalId) clearInterval(intervalId);
    }
  }

  tick();
  intervalId = setInterval(tick, 1000);
})();
