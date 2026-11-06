/* Link hub filter/search. No network calls. */
(function () {
  function init(root) {
    var tools = root.querySelector(".lh-tools");
    if (!tools) return;
    var q = tools.querySelector(".lh-q");
    var clear = tools.querySelector("[data-lh-clear]");
    var count = tools.querySelector("[data-lh-count]");
    var results = root.querySelector("[id^='lh-results']") || root;
    var items = Array.prototype.slice.call(results.querySelectorAll(".lh-item"));
    var sections = Array.prototype.slice.call(results.querySelectorAll(".lh-sec"));
    var sec = "all";
    var kind = "all";

    function setChipGroup(attr, value) {
      tools.querySelectorAll("[" + attr + "]").forEach(function (b) {
        var on = b.getAttribute(attr) === value;
        b.classList.toggle("on", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
    }

    function apply() {
      var query = (q.value || "").trim().toLowerCase();
      var shown = 0;
      items.forEach(function (li) {
        var okSec = sec === "all" || li.getAttribute("data-sec") === sec;
        var okKind = kind === "all" || li.getAttribute("data-kind") === kind;
        var okQ = !query || (li.getAttribute("data-q") || "").indexOf(query) !== -1;
        var show = okSec && okKind && okQ;
        li.hidden = !show;
        if (show) shown++;
      });
      sections.forEach(function (s) {
        var any = s.querySelectorAll(".lh-item:not([hidden])").length > 0;
        s.hidden = !any;
      });
      if (clear) clear.hidden = !(query || sec !== "all" || kind !== "all");
      if (count) {
        count.textContent = shown + " of " + items.length + " links shown";
      }
    }

    tools.addEventListener("click", function (ev) {
      var b = ev.target.closest && ev.target.closest("[data-lh-sec],[data-lh-kind],[data-lh-clear]");
      if (!b || !tools.contains(b)) return;
      if (b.hasAttribute("data-lh-clear")) {
        q.value = "";
        sec = "all";
        kind = "all";
        setChipGroup("data-lh-sec", "all");
        setChipGroup("data-lh-kind", "all");
        apply();
        q.focus();
        return;
      }
      if (b.hasAttribute("data-lh-sec")) {
        sec = b.getAttribute("data-lh-sec");
        setChipGroup("data-lh-sec", sec);
        apply();
        return;
      }
      if (b.hasAttribute("data-lh-kind")) {
        kind = b.getAttribute("data-lh-kind");
        setChipGroup("data-lh-kind", kind);
        apply();
      }
    });
    q.addEventListener("input", apply);
    apply();
  }

  function boot() {
    document.querySelectorAll("article.lh[data-lh-page], article.lh").forEach(init);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
