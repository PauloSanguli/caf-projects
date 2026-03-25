/**
 * UI de <select> alinhada ao mockup (painel flutuante, sombra, item em bege #E9E6DD).
 * Mantém o <select> para POST / Django.
 */
(function () {
  var CHEVRON =
    '<svg class="custom-select__chevron" width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path fill="currentColor" d="M6 8L1 3h10z"/></svg>';

  function closeWrap(wrap) {
    if (!wrap) return;
    var menu = wrap.querySelector(".custom-select__menu");
    var trigger = wrap.querySelector(".custom-select__trigger");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
    wrap.classList.remove("custom-select--open");
  }

  function openWrap(wrap) {
    document.querySelectorAll(".custom-select--open").forEach(function (w) {
      if (w !== wrap) closeWrap(w);
    });
    var menu = wrap.querySelector(".custom-select__menu");
    var trigger = wrap.querySelector(".custom-select__trigger");
    if (menu) menu.hidden = false;
    if (trigger) trigger.setAttribute("aria-expanded", "true");
    wrap.classList.add("custom-select--open");
  }

  function build(select) {
    if (select.dataset.customSelectDone) return;
    select.dataset.customSelectDone = "1";

    var wrap = document.createElement("div");
    wrap.className = "custom-select";

    var parent = select.parentNode;
    parent.insertBefore(wrap, select);
    wrap.appendChild(select);

    select.classList.add("custom-select__native");
    select.setAttribute("tabindex", "-1");
    select.setAttribute("aria-hidden", "true");

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "custom-select__trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    if (select.id) {
      trigger.id = select.id + "-display";
    }
    var al = select.getAttribute("aria-label");
    if (al) {
      trigger.setAttribute("aria-label", al);
    }

    var valueSpan = document.createElement("span");
    valueSpan.className = "custom-select__value";
    trigger.appendChild(valueSpan);
    trigger.insertAdjacentHTML("beforeend", CHEVRON);

    var menu = document.createElement("ul");
    menu.className = "custom-select__menu";
    menu.setAttribute("role", "listbox");
    menu.hidden = true;

    var options = select.querySelectorAll("option");
    var items = [];

    options.forEach(function (opt, idx) {
      var li = document.createElement("li");
      li.className = "custom-select__item";
      li.setAttribute("role", "option");
      li.setAttribute("data-value", opt.value);
      li.setAttribute("data-index", String(idx));
      li.textContent = opt.textContent;
      li.setAttribute("aria-selected", opt.selected ? "true" : "false");
      if (opt.selected) {
        li.classList.add("custom-select__item--selected");
      }
      menu.appendChild(li);
      items.push(li);
    });

    wrap.insertBefore(trigger, select);
    wrap.insertBefore(menu, select);
    wrap.classList.add("custom-select--ready");

    function syncTriggerText() {
      var sel = select.options[select.selectedIndex];
      if (!sel) return;
      var isPlaceholder = sel.value === "";
      valueSpan.textContent = sel.textContent;
      valueSpan.classList.toggle("custom-select__value--placeholder", isPlaceholder);
    }

    function selectIndex(index) {
      if (index < 0 || index >= select.options.length) return;
      select.selectedIndex = index;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      items.forEach(function (li, i) {
        var on = i === index;
        li.setAttribute("aria-selected", on ? "true" : "false");
        li.classList.toggle("custom-select__item--selected", on);
      });
      syncTriggerText();
      closeWrap(wrap);
    }

    select.addEventListener("change", syncTriggerText);
    syncTriggerText();

    trigger.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (wrap.classList.contains("custom-select--open")) {
        closeWrap(wrap);
      } else {
        openWrap(wrap);
      }
    });

    menu.addEventListener("click", function (e) {
      e.stopPropagation();
      var item = e.target.closest(".custom-select__item");
      if (!item) return;
      var idx = parseInt(item.getAttribute("data-index"), 10);
      selectIndex(idx);
    });

    trigger.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        if (wrap.classList.contains("custom-select--open")) {
          closeWrap(wrap);
        } else {
          openWrap(wrap);
        }
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        closeWrap(wrap);
        trigger.focus();
        return;
      }
      if (e.key === "ArrowDown") {
        e.preventDefault();
        var next = Math.min(select.selectedIndex + 1, select.options.length - 1);
        selectIndex(next);
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        var prev = Math.max(select.selectedIndex - 1, 0);
        selectIndex(prev);
      }
    });

    var label = document.querySelector('label[for="' + select.id + '"]');
    if (label && trigger.id) {
      label.setAttribute("for", trigger.id);
    }
  }

  function init() {
    document.querySelectorAll("select.js-custom-select").forEach(build);

    if (!document.documentElement.dataset.customSelectDocBound) {
      document.documentElement.dataset.customSelectDocBound = "1";
      document.addEventListener("click", function () {
        document.querySelectorAll(".custom-select--open").forEach(closeWrap);
      });
      document.addEventListener("keydown", function (e) {
        if (e.key !== "Escape") return;
        document.querySelectorAll(".custom-select--open").forEach(closeWrap);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
