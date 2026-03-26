(function () {
  var root = document.getElementById("deadline-countdown");
  if (!root) return;
  var iso = root.dataset.deadline;
  if (!iso) return;
  var deadline = new Date(iso);
  if (isNaN(deadline.getTime())) return;

  var elH = root.querySelector("[data-countdown-hours]");
  var elM = root.querySelector("[data-countdown-minutes]");
  var elS = root.querySelector("[data-countdown-seconds]");
  var unitsEl = root.querySelector(".deadline-countdown__grid");
  if (!elH || !elM || !elS) return;

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  var intervalId;

  function tick() {
    var diff = deadline - Date.now();
    var totalSeconds = Math.floor(diff / 1000);
    if (totalSeconds <= 0) {
      elH.textContent = "00";
      elM.textContent = "00";
      elS.textContent = "00";
      if (unitsEl) {
        unitsEl.setAttribute("aria-label", "Tempo restante: 00:00:00");
      }
      if (intervalId) clearInterval(intervalId);
      return;
    }
    var h = Math.floor(totalSeconds / 3600);
    var m = Math.floor((totalSeconds % 3600) / 60);
    var s = totalSeconds % 60;
    elH.textContent = pad(h);
    elM.textContent = pad(m);
    elS.textContent = pad(s);
    var aria = "Tempo restante: " + pad(h) + " horas, " + pad(m) + " minutos e " + pad(s) + " segundos";
    if (unitsEl) unitsEl.setAttribute("aria-label", aria);
  }

  tick();
  intervalId = setInterval(tick, 1000);
})();
