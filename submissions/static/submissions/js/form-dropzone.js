(function () {
  document.querySelectorAll("[data-dropzone]").forEach(function (zone) {
    var input = zone.querySelector('input[type="file"]');
    var nameEl = zone.querySelector("[data-filename]");
    var visual = zone.querySelector(".dropzone__visual");

    if (!input || !nameEl) return;

    function showName(files) {
      if (files && files.length) {
        nameEl.textContent = files[0].name;
        nameEl.hidden = false;
        if (visual) visual.classList.add("dropzone__visual--hidden");
      } else {
        nameEl.textContent = "";
        nameEl.hidden = true;
        if (visual) visual.classList.remove("dropzone__visual--hidden");
      }
    }

    if (input.files && input.files.length) {
      showName(input.files);
    }

    input.addEventListener("change", function () {
      showName(input.files);
    });

    ["dragenter", "dragover"].forEach(function (ev) {
      zone.addEventListener(ev, function (e) {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.add("dropzone--drag");
      });
    });

    ["dragleave", "drop"].forEach(function (ev) {
      zone.addEventListener(ev, function (e) {
        e.preventDefault();
        e.stopPropagation();
        zone.classList.remove("dropzone--drag");
      });
    });

    zone.addEventListener("drop", function (e) {
      var dt = e.dataTransfer;
      if (!dt || !dt.files || !dt.files.length) return;
      input.files = dt.files;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  });
})();
