"use strict";
// Figure 2: the predator-prey arms race. Reads runs/arms/index.json and runs/arms/<world>.json (darwin/arms.py + arms_index.py).
window.Arms = (() => {
const $ = (s) => document.querySelector(s);
const Q = new URLSearchParams(location.search);
const RENDER = Q.has("render");
const DPR = Math.min(window.devicePixelRatio || 1, 2);
const INK = "#141413", INK2 = "#3d3d3a", INK3 = "#73726c", INK4 = "#a19e95", HAIR = "#e8e6dc";
const PREY = "#1f8a7a", PRED = "#b5432f";
// Stream colours: the dataviz reference categorical order, validated for adjacent pairs on a light surface; bands are also labelled.
const PAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"];
const COND = [["jev", "Jev's answers", "#c96442"], ["additive", "No-interaction table", "#2a78d6"],
              ["frozen_predators", "Fixed predators", "#8a877e"], ["shuffled", "Shuffled answers", "#6250d6"]];
const RULES = { po: "Selection by predators only", default: "Selection by habitat fit and predators" };
let IDX, D, W, R, seed, G, t = 0, playing = !RENDER, speed = 25, lastTs = 0, dirty = true;
let fy, fr, streams, streamCache = {};

const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;
function rgba(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
const visible = () => { const f = $("#fig-arms"); return f && f.offsetParent !== null; };
function canvas(id) {
  const c = $(id), r = c.getBoundingClientRect(), w = Math.max(1, r.width), h = Math.max(1, r.height);
  if (c.width !== Math.round(w * DPR) || c.height !== Math.round(h * DPR)) { c.width = Math.round(w * DPR); c.height = Math.round(h * DPR); }
  const x = c.getContext("2d"); x.setTransform(DPR, 0, 0, DPR, 0, 0); return [x, w, h];
}
const freqs = (c) => { const s = c.reduce((a, b) => a + b, 0) || 1; return Float32Array.from(c, (v) => v / s); };
function at(arr, tt) {
  const g0 = Math.floor(clamp(tt, 0, G)), g1 = Math.min(g0 + 1, G), k = clamp(tt, 0, G) - g0, o = new Float32Array(64);
  for (let i = 0; i < 64; i++) o[i] = arr[g0][i] * (1 - k) + arr[g1][i] * k; return o;
}
const preyLabel = (j) => `${D.labels.escape[j >> 3]}, ${D.labels.defense[j & 7]}`;
const predLabel = (i) => `${D.labels.hunt[i >> 3]}, ${D.labels.weapon[i & 7]}`;
const preyPhrase = (j) => `${D.phrases.escape[j >> 3]}, and ${D.phrases.defense[j & 7]}`;
const predPhrase = (i) => `${D.phrases.hunt[i >> 3]}, with ${D.phrases.weapon[i & 7]}`;
const block = () => (R === "po" ? D.predation_only : D);

function seg(el, items, cur, on) {
  el.innerHTML = items.map(([v, l]) => `<button data-v="${v}" class="${String(v) === String(cur) ? "on" : ""}">${l}</button>`).join("");
  el.querySelectorAll("button").forEach((b) => b.onclick = () => on(b.dataset.v));
}
async function init() {
  IDX = await (await fetch("../runs/arms/index.json")).json();
  W = Q.get("world") || IDX.start.world; R = Q.get("rules") || IDX.start.rules; seed = Q.get("seed") || IDX.start.seed;
  $("#a-play").onclick = () => { if (!playing && t >= G) t = 0; setPlaying(!playing); };
  $("#a-range").oninput = (e) => { t = +e.target.value; dirty = true; };
  $("#a-speeds").querySelectorAll("button").forEach((b) => b.onclick = () => {
    speed = +b.dataset.s; $("#a-speeds").querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b)); });
  setPlaying(playing);
  try { await document.fonts.ready; } catch (e) {}
  await setAll(W, R, seed);
  // grid hover: read one design in full
  for (const [id, isPrey] of [["#a-preyGrid", true], ["#a-predGrid", false]]) {
    const c = $(id);
    c.addEventListener("mousemove", (e) => gridTip(e, c, isPrey));
    c.addEventListener("mouseleave", () => $("#a-tip").classList.remove("on"));
  }
  window.addEventListener("resize", () => { streamCache = {}; dirty = true; if (visible()) { drawCtrl(); drawShift(); } });
  window.__armsReady = true;
  if (!RENDER) requestAnimationFrame(loop);
}
const cacheW = {};
async function setAll(w, r, s) {
  if (!cacheW[w]) cacheW[w] = await (await fetch(`../runs/arms/${w}.json`)).json();
  W = w; R = r; seed = String(s); D = cacheW[w];
  G = D.gens; $("#a-range").max = G;
  seg($("#a-worlds"), IDX.worlds.map((m) => [m.key, m.name]), W, (v) => setAll(v, R, seed));
  seg($("#a-rules"), [["po", "Predators only"], ["default", "Habitat fit + predators"]], R, (v) => setAll(W, v, seed));
  seg($("#a-seeds"), D.seeds.map((k) => [k, `Run ${k}`]), seed, (v) => setAll(W, R, v));
  const run = D.runs[R === "po" ? `po${seed}` : seed];
  fy = run.prey.map(freqs); fr = run.pred.map(freqs);
  streams = { prey: slotShares(fy), pred: slotShares(fr) }; streamCache = {};
  const m = IDX.worlds.find((q) => q.key === W);
  const p = R === "po" ? "A prey animal breeds if it is not caught; each predator makes 15 attacks per generation."
                       : "Breeding is also weighted by Jev's habitat-fit score (could this animal find food and raise young here?); each predator makes 5 attacks per generation.";
  $("#a-note").innerHTML = `<b>${m.name}.</b> ${D.state} <span class="rules"><b>${RULES[R]}:</b> ${p}</span>`;
  $("#a-rset").textContent = R === "po" ? "selection by predators only" : "selection by habitat fit and predators";
  dirty = true;
  if (visible()) { drawCtrl(); drawShift(); drawNow(); }
}

// ---------- 8x8 grids: dot area = share of the population; cell shade = how deadly that design is (or how often it dies) against the other side now
let gridGeom = {};
function drawGrid(id, f, other, isPrey) {
  const [x, w, h] = canvas(id);
  x.clearRect(0, 0, w, h);
  const rowL = isPrey ? D.labels.escape : D.labels.hunt, colL = isPrey ? D.labels.defense : D.labels.weapon;
  const fs = w < 340 ? 10 : 11;
  x.font = `600 ${fs}px Inter`;
  const rw = Math.max(...rowL.map((l) => x.measureText(l).width)), cw = Math.max(...colL.map((l) => x.measureText(l).width)) * 0.71;
  const padL = rw + 12, padT = cw + 14;
  let cs = Math.min((w - padL - 4) / 8, (h - padT - 4) / 8);
  const over = Math.max(0, cw - 6 - cs / 2); if (padL + 8 * cs + over > w) cs = (w - padL - over) / 8;
  gridGeom[id] = { padL, padT, cs };
  const val = new Float32Array(64);
  for (let a = 0; a < 64; a++) {
    let s = 0;
    for (let b = 0; b < 64; b++) { if (other[b] < 1e-4) continue; s += other[b] * (isPrey ? D.hunt_p[b][a] : D.hunt_p[a][b]); }
    val[a] = s;
  }
  let lo = Infinity, hi = -Infinity; for (const v of val) { lo = Math.min(lo, v); hi = Math.max(hi, v); }
  x.font = `${fs}px Inter`; x.textBaseline = "middle";
  let topR = 0; for (let k = 1; k < 64; k++) if (f[k] > f[topR]) topR = k;
  for (let r = 0; r < 8; r++) {
    const on = (topR >> 3) === r; x.font = `${on ? 600 : 400} ${fs}px Inter`;
    x.fillStyle = on ? INK : INK3; x.textAlign = "right"; x.fillText(rowL[r], padL - 8, padT + r * cs + cs / 2);
  }
  for (let c = 0; c < 8; c++) {
    const on = (topR & 7) === c; x.font = `${on ? 600 : 400} ${fs}px Inter`;
    x.save(); x.translate(padL + c * cs + cs / 2 - 3, padT - 8); x.rotate(-Math.PI / 4);
    x.fillStyle = on ? INK : INK3; x.textAlign = "left"; x.fillText(colL[c], 0, 0); x.restore();
  }
  const shade = isPrey ? PRED : "#c9862b";
  for (let k = 0; k < 64; k++) {
    const r = k >> 3, c = k & 7, cx = padL + c * cs, cy = padT + r * cs;
    const v = (val[k] - lo) / (hi - lo || 1);
    x.fillStyle = "#f4f2ec"; x.beginPath(); x.roundRect(cx + 1, cy + 1, cs - 2, cs - 2, 3); x.fill();
    x.fillStyle = rgba(shade, 0.04 + 0.5 * v * v); x.beginPath(); x.roundRect(cx + 1, cy + 1, cs - 2, cs - 2, 3); x.fill();
  }
  const col = isPrey ? PREY : PRED;
  for (let k = 0; k < 64; k++) {
    if (f[k] < 0.002) continue;
    const r = k >> 3, c = k & 7, cx = padL + c * cs + cs / 2, cy = padT + r * cs + cs / 2;
    const rad = Math.max(1.8, Math.sqrt(f[k]) * cs * 0.62);
    x.fillStyle = col; x.strokeStyle = "#ffffff"; x.lineWidth = 1.5; x.beginPath(); x.arc(cx, cy, rad, 0, 7); x.fill(); x.stroke();
  }
  return val;
}
let lastPy, lastPr, lastThreat, lastPredVal;
function gridTip(e, c, isPrey) {
  const g = gridGeom["#" + c.id]; if (!g || !lastPy) return;
  const r = c.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
  const col = Math.floor((mx - g.padL) / g.cs), row = Math.floor((my - g.padT) / g.cs), tip = $("#a-tip");
  if (col < 0 || col > 7 || row < 0 || row > 7) { tip.classList.remove("on"); return; }
  const k = row * 8 + col, f = isPrey ? lastPy : lastPr, v = isPrey ? lastThreat : lastPredVal;
  tip.innerHTML = isPrey
    ? `<b>${preyLabel(k)}</b><div class="m">${preyPhrase(k)}</div><div>${(f[k] * 100).toFixed(1)}% of prey · an attack by today's predators kills it ${(v[k] * 100).toFixed(0)}% of the time</div>`
    : `<b>${predLabel(k)}</b><div class="m">${predPhrase(k)}</div><div>${(f[k] * 100).toFixed(1)}% of predators · kills today's prey on ${(v[k] * 100).toFixed(0)}% of attacks</div>`;
  const host = c.closest(".cv").getBoundingClientRect();
  tip.classList.add("on");
  const tw = Math.min(280, window.innerWidth - 32); tip.style.width = tw + "px";
  let left = e.clientX + 14; if (left + tw > window.innerWidth - 12) left = e.clientX - tw - 14;
  tip.style.left = Math.max(12, left) + "px"; tip.style.top = (e.clientY + 14) + "px";
  void host;
}

// ---------- streams: stacked share of each first-slot phrase over time; the static part is cached, the playhead drawn on top
function slotShares(arr) { return arr.map((f) => { const v = new Float32Array(8); for (let k = 0; k < 64; k++) v[k >> 3] += f[k]; return v; }); }
function streamBase(id, S, labels, w, h) {
  const key = `${id}|${W}|${R}|${seed}|${w}x${h}`;
  if (streamCache[id] && streamCache[id].key === key) return streamCache[id].cv;
  const cv = document.createElement("canvas"); cv.width = Math.round(w * DPR); cv.height = Math.round(h * DPR);
  const x = cv.getContext("2d"); x.scale(DPR, DPR);
  const X = (g) => (g / G) * w, top = 0, H = h - 20;
  for (let s = 0; s < 8; s++) {
    x.beginPath();
    for (let g = 0; g <= G; g++) { let y0 = 0; for (let q = 0; q < s; q++) y0 += S[g][q]; x.lineTo(X(g), top + H * y0); }
    for (let g = G; g >= 0; g--) { let y1 = 0; for (let q = 0; q <= s; q++) y1 += S[g][q]; x.lineTo(X(g), top + H * y1); }
    x.closePath(); x.fillStyle = PAL[s]; x.fill();
    x.strokeStyle = "#ffffff"; x.lineWidth = 0.8; x.stroke();
  }
  x.font = "500 11px Inter"; x.textAlign = "center"; x.textBaseline = "middle";
  const placed = [];
  for (let s = 0; s < 8; s++) {
    const step = Math.max(40, Math.round(G / Math.max(3, Math.floor(w / 140))));
    for (let g0 = 0; g0 < G; g0 += step) {
      let best = -1, bg = 0;
      for (let g = Math.max(g0, 6); g < Math.min(g0 + step, G - 6); g++) if (S[g][s] > best) { best = S[g][s]; bg = g; }
      if (best < 0.18) continue;
      let y0 = 0; for (let q = 0; q < s; q++) y0 += S[bg][q];
      const tw = x.measureText(labels[s]).width / 2 + 6, px = clamp(X(bg), tw, w - tw), py = top + H * (y0 + best / 2);
      if (placed.some(([a, b]) => Math.abs(a - px) < 110 && Math.abs(b - py) < 16)) continue;
      placed.push([px, py]);
      x.fillStyle = "rgba(255,255,255,.88)"; x.beginPath(); x.roundRect(px - tw, py - 8, tw * 2, 16, 4); x.fill();
      x.fillStyle = INK; x.fillText(labels[s], px, py);
    }
  }
  x.fillStyle = INK3; x.font = "10.5px Inter"; x.textBaseline = "alphabetic";
  for (let g = 0; g <= G; g += 100) { x.textAlign = g === 0 ? "left" : g === G ? "right" : "center"; x.fillText(g === 0 ? (w < 500 ? "0" : "Generation 0") : String(g), X(g), h - 4); }
  streamCache[id] = { key, cv };
  return cv;
}
function drawStream(id, S, labels) {
  const [x, w, h] = canvas(id);
  x.clearRect(0, 0, w, h);
  x.drawImage(streamBase(id, S, labels, w, h), 0, 0, w, h);
  const cx = (t / G) * w, H = h - 20;
  x.fillStyle = "rgba(255,255,255,.72)"; x.fillRect(cx, 0, w - cx, H);
  x.strokeStyle = INK; x.lineWidth = 1.5; x.beginPath(); x.moveTo(cx, 0); x.lineTo(cx, H); x.stroke();
}

// ---------- prey switches per seed, per condition
function drawCtrl() {
  const [x, w, h] = canvas("#a-ctrl");
  x.clearRect(0, 0, w, h);
  const C = block().conditions, rh = (h - 22) / COND.length, x0 = w < 400 ? 124 : 140, bw = w - x0 - 44;
  const vmax = Math.max(10, ...COND.flatMap(([k]) => C[k].map((r) => r.prey_turnovers)));
  const X = (v) => x0 + (v / vmax) * bw;
  x.strokeStyle = HAIR; x.fillStyle = INK3; x.font = "10.5px Inter"; x.textAlign = "center"; x.lineWidth = 1;
  for (let v = 0; v <= vmax; v += 5) { x.beginPath(); x.moveTo(X(v), 0); x.lineTo(X(v), h - 18); x.stroke(); x.fillText(v, X(v), h - 4); }
  COND.forEach(([k, lab, col], i) => {
    const y = i * rh + rh / 2, v = C[k].map((r) => r.prey_turnovers), m = mean(v);
    x.font = (k === "jev" ? "600 " : "") + "12px Inter"; x.textAlign = "right"; x.textBaseline = "middle";
    x.fillStyle = k === "jev" ? INK : INK2; x.fillText(lab, x0 - 10, y);
    x.fillStyle = rgba(col, 0.16); x.beginPath(); x.roundRect(x0, y - 8, Math.max(2, X(m) - x0), 16, 3); x.fill();
    v.forEach((vv, n) => { x.fillStyle = col; x.strokeStyle = "#fff"; x.lineWidth = 1.5; x.beginPath(); x.arc(X(vv), y + (n - 2) * 2.4, 4, 0, 7); x.fill(); x.stroke(); });
    x.fillStyle = INK; x.textAlign = "left"; x.font = "500 11.5px Inter"; x.fillText(m.toFixed(1), X(vmax) + 8, y);
  });
  x.textBaseline = "alphabetic";
}

// ---------- time-shift: kill rate of predators from t+tau against prey from t, minus tau = 0, mean over seeds
function shiftCurve(k) {
  const rs = block().conditions[k].map((r) => r.time_shift);
  return rs[0].map((p, i) => { const v = mean(rs.map((r) => r[i][1] - r.find((q) => q[0] === 0)[1])); return [p[0], v * 100]; });
}
function drawShift() {
  const [x, w, h] = canvas("#a-shift");
  x.clearRect(0, 0, w, h);
  const curves = COND.map(([k, lab, col]) => ({ k, lab, col, pts: shiftCurve(k) }));
  const amax = Math.max(0.5, ...curves.flatMap((c) => c.pts.map((p) => Math.abs(p[1])))) * 1.12;
  const padL = 40, padR = w < 400 ? 120 : 124, X = (tau) => padL + ((tau + 40) / 80) * (w - padL - padR), Y = (v) => (h - 20) / 2 - (v / amax) * ((h - 32) / 2);
  x.strokeStyle = HAIR; x.lineWidth = 1;
  x.beginPath(); x.moveTo(X(0), 4); x.lineTo(X(0), h - 20); x.moveTo(padL, Y(0)); x.lineTo(w - padR, Y(0)); x.stroke();
  x.font = "10.5px Inter"; x.fillStyle = INK3; x.textAlign = "center"; x.textBaseline = "alphabetic";
  for (const tau of [-40, -20, 0, 20, 40]) x.fillText(tau > 0 ? `+${tau}` : `${tau}`, X(tau), h - 4);
  x.textAlign = "right"; x.fillText(`+${amax.toFixed(1)} pp`, padL - 4, 12); x.fillText(`−${amax.toFixed(1)}`, padL - 4, h - 24); x.fillText("0", padL - 4, Y(0) + 4);
  x.textAlign = "left"; x.fillText("← predators from the past", padL + 4, h - 24);
  x.textAlign = "right"; x.fillText("from the future →", w - padR - 4, 12);
  const ends = [];
  for (const c of curves) {
    x.strokeStyle = c.col; x.lineWidth = c.k === "jev" ? 2.5 : 1.6; x.setLineDash(c.k === "shuffled" ? [4, 4] : []);
    x.beginPath(); c.pts.forEach(([tau, v], i) => (i ? x.lineTo(X(tau), Y(v)) : x.moveTo(X(tau), Y(v)))); x.stroke();
    ends.push([c, Y(c.pts[c.pts.length - 1][1])]);
  }
  x.setLineDash([]);
  ends.sort((a, b) => a[1] - b[1]);
  let last = -99;
  for (const [c, yy] of ends) {
    const y = Math.max(yy, last + 14); last = y;
    x.fillStyle = c.col; x.beginPath(); x.arc(w - padR + 8, y, 3, 0, 7); x.fill();
    x.fillStyle = c.k === "jev" ? INK : INK2; x.font = (c.k === "jev" ? "600 " : "") + "11px Inter"; x.textAlign = "left"; x.textBaseline = "middle";
    x.fillText(c.lab, w - padR + 15, y);
  }
  x.textBaseline = "alphabetic";
  const C = block().conditions, gap = (k) => C[k].map((r) => { const d = Object.fromEntries(r.time_shift); return 100 * (d[20] - d[-20]); });
  const gj = gap("jev"), ga = gap("additive"), gf = gap("frozen_predators");
  const pos = gj.filter((v) => v > 0).length;
  $("#a-shiftnote").innerHTML = `Predators from 20 generations later minus predators from 20 generations earlier, against the same prey: <b>${fmtR(gj)}</b> percentage points with Jev's answers (${pos} of ${gj.length} runs above 0), ${fmtR(ga)} with the no-interaction table, ${fmtR(gf)} with fixed predators.`;
  const sw = (k) => C[k].map((r) => r.prey_turnovers).join(", ");
  $("#a-ctrlnote").innerHTML = `How many times the most common prey design changes after generation 100, in each of the 5 runs (dots; bar = mean). Jev's answers: <b>${sw("jev")}</b>. No-interaction table: ${sw("additive")}. Fixed predators: ${sw("frozen_predators")}. Shuffled answers: ${sw("shuffled")}.`;
}
function fmtR(a) { const lo = Math.min(...a), hi = Math.max(...a), f = (v) => (v >= 0 ? "+" : "−") + Math.abs(v).toFixed(2); return `${f(lo)} to ${f(hi)}`; }

function drawNow() {
  const py = at(fy, t), pr = at(fr, t);
  const threat = drawGrid("#a-preyGrid", py, pr, true);
  lastPredVal = drawGrid("#a-predGrid", pr, py, false);
  lastPy = py; lastPr = pr; lastThreat = threat;
  let jy = 0, ir = 0; for (let k = 1; k < 64; k++) { if (py[k] > py[jy]) jy = k; if (pr[k] > pr[ir]) ir = k; }
  let kill = 0; for (let j = 0; j < 64; j++) kill += py[j] * threat[j];
  $("#a-now").innerHTML =
    `<div class="k">Most common prey · ${(py[jy] * 100).toFixed(0)}%</div><div class="v"><i class="dot" style="background:${PREY}"></i>${preyLabel(jy)}</div><div class="ph">${preyPhrase(jy)}</div>` +
    `<div class="k">Most common predator · ${(pr[ir] * 100).toFixed(0)}%</div><div class="v"><i class="dot" style="background:${PRED}"></i>${predLabel(ir)}</div><div class="ph">${predPhrase(ir)}</div>` +
    `<div class="k">Chance one attack kills</div><div class="big">${(kill * 100).toFixed(1)}%</div>`;
  $("#a-gen").textContent = `Generation ${Math.floor(t)} of ${G}`;
  drawStream("#a-preyStream", streams.prey, D.labels.escape);
  drawStream("#a-predStream", streams.pred, D.labels.hunt);
}
function setPlaying(p) { playing = p; $("#a-play").innerHTML = p ? PAUSE : PLAY; $("#a-play").setAttribute("aria-label", p ? "Pause" : "Play"); }
const PLAY = '<svg viewBox="0 0 12 12"><path d="M2.5 1.2v9.6L10.6 6z" fill="currentColor"/></svg>';
const PAUSE = '<svg viewBox="0 0 12 12"><rect x="2" y="1.5" width="2.8" height="9" rx=".6" fill="currentColor"/><rect x="7.2" y="1.5" width="2.8" height="9" rx=".6" fill="currentColor"/></svg>';

function loop(ts) {
  const dt = lastTs ? Math.min((ts - lastTs) / 1000, 0.1) : 0; lastTs = ts;
  if (D && visible()) {
    if (playing) {
      t += dt * speed; dirty = true;
      if (t >= G) { t = G; setPlaying(false); }
      if (document.activeElement !== $("#a-range")) $("#a-range").value = t;
    }
    if (dirty) { drawNow(); dirty = false; }
  }
  requestAnimationFrame(loop);
}

// render hooks used by darwin/render_arms.py
return {
  init,
  onShow() { streamCache = {}; dirty = true; if (D) { drawCtrl(); drawShift(); drawNow(); } },
  setT(tt) { t = tt; $("#a-range").value = t; drawNow(); },
  set: (w, r, s) => setAll(w, r, s),
  caption(html) { const c = $("#a-cap"); c.innerHTML = html || ""; c.classList.toggle("on", !!html); },
};
})();
