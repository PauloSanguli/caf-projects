/**
 * Mostra overlay de carregamento ao submeter formulários (GET ou POST)
 * até a nova página ser renderizada.
 */
(function () {
  "use strict";

  function hideAll() {
    document.querySelectorAll(".page-loading[data-page-loading]").forEach(function (el) {
      el.hidden = true;
      el.setAttribute("aria-hidden", "true");
      el.removeAttribute("aria-busy");
      var box = el.querySelector(".page-loading__box");
      if (box) box.removeAttribute("aria-busy");
    });
    document.body.classList.remove("page-loading--active");
  }

  function init() {
    document.querySelectorAll("form[data-loading-overlay]").forEach(function (form) {
      var id = form.getAttribute("data-loading-overlay");
      if (!id) return;
      var overlay = document.getElementById(id);
      if (!overlay) return;
      form.addEventListener("submit", function () {
        overlay.hidden = false;
        overlay.removeAttribute("aria-hidden");
        overlay.setAttribute("aria-busy", "true");
        var box = overlay.querySelector(".page-loading__box");
        if (box) box.setAttribute("aria-busy", "true");
        document.body.classList.add("page-loading--active");
      });
    });
  }

  window.addEventListener("pageshow", hideAll);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
