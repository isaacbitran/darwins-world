"use strict";
// Study page shell: two parts as tabs (one visible at a time, so only one figure animates), deep links #islands / #arms.
(() => {
  const PARTS = ["islands", "arms"];
  if (new URLSearchParams(location.search).has("render")) document.documentElement.classList.add("render");
  const started = {};
  function show(p, scroll) {
    if (!PARTS.includes(p)) p = "islands";
    document.querySelectorAll(".part").forEach((s) => s.classList.toggle("on", s.id === `part-${p}`));
    document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.p === p));
    if (location.hash !== `#${p}`) history.replaceState(null, "", `${location.search}#${p}`);
    const mod = p === "islands" ? window.Islands : window.Arms;
    if (!started[p]) started[p] = mod.init(); else mod.onShow();
    started[p].then?.(() => mod.onShow());
    if (scroll) document.getElementById(`part-${p}`).scrollIntoView({ behavior: "smooth", block: "start" });
  }
  document.querySelectorAll("[data-p]").forEach((el) => el.addEventListener("click", (e) => {
    e.preventDefault(); show(el.dataset.p, el.closest(".contents") != null);
  }));
  window.addEventListener("keydown", (e) => {
    if (e.code !== "Space" || /INPUT|SELECT|TEXTAREA|BUTTON|SUMMARY/.test(e.target.tagName)) return;
    e.preventDefault();
    const on = document.querySelector(".part.on");
    on && on.querySelector(".play").click();
  });
  window.__show = show;
  show(location.hash.slice(1), false);
})();
