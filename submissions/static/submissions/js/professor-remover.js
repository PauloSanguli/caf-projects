/**
 * Confirmação integrada antes de remover grupo (substitui window.confirm).
 */
(function () {
  "use strict";

  var dialog = document.getElementById("dialog-remover-grupo");
  if (!dialog) return;

  var backdrop = dialog.querySelector(".confirm-dialog__backdrop");
  var btnCancel = dialog.querySelector("[data-action='cancel']");
  var btnConfirm = dialog.querySelector("[data-action='confirm']");
  var titleEl = dialog.querySelector("[data-dialog-title]");
  var pendingForm = null;
  var lastFocus = null;

  function open(form) {
    pendingForm = form;
    lastFocus = document.activeElement;
    var label = form.getAttribute("data-remover-label") || "este grupo";
    if (titleEl) {
      titleEl.textContent = "Remover «" + label + "»?";
    }
    dialog.hidden = false;
    document.body.classList.add("confirm-dialog-open");
    btnConfirm.focus();
  }

  function close() {
    dialog.hidden = true;
    document.body.classList.remove("confirm-dialog-open");
    pendingForm = null;
    if (lastFocus && typeof lastFocus.focus === "function") {
      lastFocus.focus();
    }
  }

  function confirmRemove() {
    if (!pendingForm) return;
    var form = pendingForm;
    pendingForm = null;
    dialog.hidden = true;
    document.body.classList.remove("confirm-dialog-open");
    form.dataset.confirmed = "1";
    if (typeof form.requestSubmit === "function") {
      form.requestSubmit();
    } else {
      form.submit();
    }
  }

  document.querySelectorAll("form.form-remover-grupo").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (form.dataset.confirmed === "1") {
        delete form.dataset.confirmed;
        return;
      }
      e.preventDefault();
      open(form);
    });
  });

  if (btnCancel) btnCancel.addEventListener("click", close);
  if (btnConfirm) btnConfirm.addEventListener("click", confirmRemove);
  if (backdrop) backdrop.addEventListener("click", close);

  dialog.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      e.preventDefault();
      close();
    }
  });

  if (btnConfirm && btnCancel) {
    btnConfirm.addEventListener("keydown", function (e) {
      if (e.key === "Tab" && e.shiftKey) {
        e.preventDefault();
        btnCancel.focus();
      }
    });
    btnCancel.addEventListener("keydown", function (e) {
      if (e.key === "Tab" && !e.shiftKey) {
        e.preventDefault();
        btnConfirm.focus();
      }
    });
  }
})();
