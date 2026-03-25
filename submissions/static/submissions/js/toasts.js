/**
 * Mensagens Django (.messages--toast): posição fixa, entrada suave e auto-dismiss.
 */
(function () {
  "use strict";

  var SUCCESS_MS = 5500;
  var ERROR_MS = 9000;

  function dismiss(el) {
    if (!el || el.classList.contains("msg--dismissing")) return;
    el.classList.add("msg--dismissing");
    window.setTimeout(function () {
      el.remove();
    }, 320);
  }

  function init() {
    var stack = document.querySelector(".messages--toast");
    if (!stack) return;

    stack.querySelectorAll(".msg").forEach(function (msg) {
      var isError = msg.classList.contains("msg-error");
      var delay = isError ? ERROR_MS : SUCCESS_MS;
      var t = window.setTimeout(function () {
        dismiss(msg);
      }, delay);

      var close = document.createElement("button");
      close.type = "button";
      close.className = "msg__close";
      close.setAttribute("aria-label", "Fechar");
      close.innerHTML =
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9 9l6 6M15 9l-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
      close.addEventListener("click", function () {
        window.clearTimeout(t);
        dismiss(msg);
      });
      msg.appendChild(close);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
