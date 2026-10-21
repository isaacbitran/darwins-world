"use strict";
// Figure 1: the seven islands. Reads runs/seedN.json (darwin/sim.py) and runs/summary.json (darwin/summarize.py).
window.Islands = (() => {
const $ = (s) => document.querySelector(s);
const Q = new URLSearchParams(location.search);
const RENDER = Q.has("render");
const DPR = Math.min(window.devicePixelRatio || 1, 2);
const INK = "#141413", INK2 = "#3d3d3a", INK3 = "#73726c", INK4 = "#a19e95", RED = "#b5432f";
// Island hues: validated with the dataviz palette checker against a light surface (adjacent pairs, CVD and normal vision).
// Display names: plain habitat names. The Jev prompts in darwin/islands.py also use a short proper name (e.g. "Frostholm").
const ISL_NAME = { tundra: "Tundra", ocean: "Open ocean", rainforest: "Rainforest", grassland: "Savanna", desert: "Desert", volcanic: "Volcano", cave: "Caves" };
const ISL_COLOR = { tundra: "#2a78d6", ocean: "#1baf7a", rainforest: "#008300", grassland: "#d4b000", desert: "#eb6834", volcanic: "#b0303a", cave: "#6250d6" };

// ---------- palette for colour traits (label -> hex), as the creature would look
const COLORS = {
  "snow-white": "#f4f8ff", cream: "#f3e8cf", silver: "#c9d3e3", seasonal: "#e8e1d0", "sand-colored": "#e6c690", ochre: "#d9a43c",
  "rust-brown": "#b8643a", speckled: "#d8c4a0", black: "#3a3d4a", charcoal: "#5f6372", midnight: "#2c3f8c", sooty: "#5e4b44",
  brown: "#8a5a3c", "leaf-green": "#4cc75b", "moss-green": "#6f9e4c", emerald: "#1fbf82", olive: "#8a903c", scarlet: "#e8293d",
  "tiger-striped": "#f07a1a", "electric-blue": "#1fa0ec", neon: "#d8e626", iridescent: "#9b52ea", pink: "#f06aa8", rainbow: "#ee55c4",
  spotted: "#9a9fac", golden: "#e6a92e", "fox-red": "#ef5a1a", "sea-grey": "#6f93b2", countershaded: "#4f76c8", silvery: "#cbd9e8",
  clear: "#b4e2fa", unpigmented: "#ece6f3", "mud-brown": "#7c6348", "zebra-striped": "#d6d6d6", "ash-grey": "#7e7e86",
  "black-and-red": "#c8243a", lemon: "#f2df4a", cinnamon: "#b76b35", cobalt: "#2f5fef", "bark-colored": "#7f6a42",
  "forest-green": "#1f8e4a", starry: "#5a98ea", "ember-red": "#ef4a26", "grass-colored": "#b29c64", ermine: "#f4f4f8",
  "snow-mottled": "#d2d8e2", toadstool: "#ee3a3a", "ice-blue": "#c4e6fa",
};
const FEAT_LABEL = { insul: "insulating coat", fur: "fur", blubber: "blubber", feathers: "feathers", scales: "scales", armor: "armor or shell",
  bare: "bare skin", white: "white or pale", sandy: "sand-colored", dark: "dark-colored", green: "green", bright: "bright colors", sea: "sea colors",
  big: "large body", small: "small body", aquatic: "swims", fly: "flies", burrow: "burrows", climb: "climbs", run: "runs fast", noct: "nocturnal",
  day: "active by day", water: "saves water", heat: "heat-tolerant", cold: "cold-adapted", cave: "cave senses", herb: "plant-eater",
  carn: "meat-eater", filter: "filter-feeder", scav: "scavenger", omni: "omnivore", social: "social", defense: "defenses" };
const SLOT_NAME = ["size", "coat", "colour", "diet", "moves", "active", "behaviour", "body"];
const CAUSE = ["", "eaten", "starved", "could not live in this habitat", "killed by the harsh season", "old age"];

let D, P, G, NI, ISL, alive, diedAt, nC, cr, spById, shownSp, events, spIslCounts, traitCnt;
let clk = 0, t = 0, playing = !RENDER, speed = 1, lastTs = 0, hover = -1, pinned = -1, seed = +(Q.get("seed") || 1);
let seeds = [1], mode = "map", webIsl = 0, summary = null, loading = false;

// ---------- helpers
const hash = (n) => { n = (n ^ 61) ^ (n >>> 16); n = n + (n << 3); n = n ^ (n >>> 4); n = Math.imul(n, 0x27d4eb2d); n = n ^ (n >>> 15); return (n >>> 0) / 4294967296; };
const h2 = (a, b) => hash(Math.imul(a + 1, 73856093) ^ Math.imul(b + 7, 19349663));
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const ease = (x) => x < 0 ? 0 : x > 1 ? 1 : x * x * (3 - 2 * x);
function rgba(hex, a) { const n = parseInt(hex.slice(1), 16); return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`; }
const visible = () => { const f = $("#fig-islands"); return f && f.offsetParent !== null; };

// ---------- load
async function load(s) {
  loading = true;
  const r = await fetch(`../runs/seed${s}.json`); D = await r.json();
  P = D.meta.pool; G = D.meta.gens; ISL = D.meta.islands.map((i) => ({ ...i, name: ISL_NAME[i.key] || i.name, color: ISL_COLOR[i.key] || i.color })); NI = ISL.length;
  cr = D.creatures; nC = cr.length;
  alive = Array.from({ length: G + 1 }, () => []); diedAt = Array.from({ length: G + 2 }, () => []);
  for (let i = 0; i < nC; i++) {
    const c = cr[i], b = c[10], d = c[11] < 0 ? G + 1 : c[11];
    for (let g = b; g < d && g <= G; g++) alive[g].push(i);
    if (c[11] >= 0) diedAt[c[11]].push(i);
  }
  spById = new Map(D.species.map((s) => [s.id, s]));
  const NP = P.length; traitCnt = new Uint16Array((G + 1) * NI * NP); const pop = new Uint16Array((G + 1) * NI);
  spIslCounts = new Map();
  for (let g = 0; g <= G; g++) for (const i of alive[g]) {
    const c = cr[i], isl = islAt(c, g + 0.99); pop[g * NI + isl]++;
    for (let k = 1; k <= 8; k++) traitCnt[(g * NI + isl) * NP + c[k]]++;
    const key = c[16] * 8 + isl; let a = spIslCounts.get(key); if (!a) spIslCounts.set(key, a = new Uint16Array(G + 1)); a[g]++;
  }
  D.pop = pop;
  prepCreatures(); homeCache = new Map(); staticCanvas = null;
  buildEvents(); buildTree(); buildCards(); resize();
  $("#i-range").max = G;
  loading = false;
}
function islAt(c, tt) { let isl = c[9]; for (const [g, to] of c[17]) if (tt >= g) isl = to; return isl; }

// ---------- events (shown under the map)
function buildEvents() {
  events = [];
  const NP = P.length;
  const f = (g, isl, id) => traitCnt[(g * NI + isl) * NP + id] / Math.max(D.pop[g * NI + isl], 1);
  for (let isl = 0; isl < NI; isl++) {
    const cand = [];
    for (let id = 0; id < NP; id++) { const end = f(G, isl, id); if (end > 0.35) cand.push([end - f(0, isl, id), id]); }
    cand.sort((a, b) => b[0] - a[0]);
    const slots = new Set(); let n = 0;
    for (const [, id] of cand) {
      if (slots.has(P[id][2]) || n === 3) continue; slots.add(P[id][2]); n++;
      for (let g = 1; g <= G; g++) if (f(g, isl, id) >= 0.5) { events.push({ g, isl, txt: `${ISL[isl].name}: <b>${P[id][1]}</b> reaches half the island`, kind: "trait" }); break; }
    }
  }
  for (const s of D.species) if (s.ext && s.peak >= 45) events.push({ g: s.ext, isl: s.isl, txt: `Extinct: ${s.name} (peak ${s.peak})`, kind: "ext" });
  for (const [key, arr] of spIslCounts) {
    const sp = Math.floor(key / 8), isl = key % 8, s = spById.get(sp);
    if (!s || s.isl === isl) continue;
    for (let g = 1; g <= G; g++) if (arr[g] >= 25) { events.push({ g, isl, txt: `Invasion: ${s.name} from ${ISL[s.isl].name} takes hold on ${ISL[isl].name}`, kind: "inv" }); break; }
  }
  for (let isl = 0; isl < NI; isl++) for (let g = 1; g <= G; g++) if (D.pop[g * NI + isl] === 0 && D.pop[(g - 1) * NI + isl] > 0) events.push({ g, isl, txt: `${ISL[isl].name} is empty: every lineage died out`, kind: "ext" });
  events.sort((a, b) => a.g - b.g);
}

// ---------- map geometry
let map, mctx, MW = 1, MH = 1, S, SX, OX, OY, staticCanvas, blobs = [];
function blobR(isl, a) { const k = isl * 1.7; return 1 + 0.07 * Math.sin(3 * a + k) + 0.045 * Math.sin(5 * a + 2 * k) + 0.025 * Math.sin(9 * a + 3 * k) + 0.012 * Math.sin(17 * a + k); }
function W(x, y) { return [OX + (x - 0.5) * SX, OY + y * S]; }
function fit(cv) {
  const r = cv.getBoundingClientRect(); const w = Math.max(1, r.width), h = Math.max(1, r.height);
  if (cv.width !== Math.round(w * DPR) || cv.height !== Math.round(h * DPR)) { cv.width = Math.round(w * DPR); cv.height = Math.round(h * DPR); }
  return [w, h];
}
function resize() {
  if (!D || !visible()) return;
  if (mode !== "map") { drawWide(); return render(); }
  [MW, MH] = fit(map);
  S = Math.min(MW / 0.98, (MH - 64) / 1.06); SX = Math.min(MW * 0.86, S * 1.32); OX = MW / 2; OY = 26;
  homeCache = new Map(); drawStatic(); sizeTree();
  render();
}
function drawStatic() {
  staticCanvas = document.createElement("canvas"); staticCanvas.width = MW * DPR; staticCanvas.height = MH * DPR;
  const c = staticCanvas.getContext("2d"); c.scale(DPR, DPR);
  c.fillStyle = "#ffffff"; c.fillRect(0, 0, MW, MH);
  c.strokeStyle = "rgba(20,20,19,0.035)"; c.lineWidth = 1;
  for (let k = 1; k < 9; k++) { c.beginPath(); c.arc(MW / 2, OY + S * 0.5, S * 0.07 * k, 0, 7); c.stroke(); }
  // migration routes
  const keys = ISL.map((i) => i.key);
  c.setLineDash([2, 5]); c.strokeStyle = "rgba(20,20,19,0.16)";
  const NB = { tundra: ["ocean", "volcanic"], ocean: ["rainforest"], rainforest: ["grassland"], grassland: ["desert"], desert: ["volcanic"] };
  for (const [a, bs] of Object.entries(NB)) for (const b of bs) {
    const A = ISL[keys.indexOf(a)], B = ISL[keys.indexOf(b)]; const [x1, y1] = W(...A.xy), [x2, y2] = W(...B.xy);
    c.beginPath(); c.moveTo(x1, y1); c.quadraticCurveTo((x1 + x2) / 2 + (MW / 2 - (x1 + x2) / 2) * -0.25, (y1 + y2) / 2 + (OY + S * 0.5 - (y1 + y2) / 2) * -0.25, x2, y2); c.stroke();
  }
  for (const isl of ISL.slice(0, 6)) { const [x1, y1] = W(...isl.xy), [x2, y2] = W(...ISL[6].xy); c.beginPath(); c.moveTo(x1, y1); c.lineTo(x2, y2); c.stroke(); }
  c.setLineDash([]);
  blobs = [];
  ISL.forEach((isl, i) => {
    const [cx, cy] = W(...isl.xy), R = isl.r * S * 1.22;
    const path = (sc) => { c.beginPath(); for (let k = 0; k <= 120; k++) { const a = k / 120 * Math.PI * 2, rr = R * sc * blobR(i, a); const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr; k ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); };
    path(1); c.fillStyle = rgba(isl.color, 0.09); c.fill();
    c.strokeStyle = rgba(isl.color, 0.75); c.lineWidth = 1.4; path(1); c.stroke();
    for (const sc of [0.75, 0.5]) { c.strokeStyle = rgba(isl.color, 0.12); c.lineWidth = 1; path(sc); c.stroke(); }
    blobs.push({ cx, cy, R });
  });
}

// ---------- creature glyphs: shape = coat type, fill = the creature's colour, thin ink outline so pale creatures stay visible
const SPR = new Map();
function shapeOf(c) {
  const tg = P[c[2]][3];
  if (/armor/.test(tg)) return "hex"; if (/feathers/.test(tg)) return "tri"; if (/blubber/.test(tg)) return "oval";
  if (/scales/.test(tg)) return "dia"; if (/fur/.test(tg)) return "fur"; return "dot";
}
// px: sprite size in device pixels, so drawing it needs no rescaling (much faster without a GPU)
function sprite(shape, hex, px = 64) {
  const key = shape + hex + px; let s = SPR.get(key); if (s) return s;
  const N = 64; s = document.createElement("canvas"); s.width = s.height = px; const c = s.getContext("2d");
  c.scale(px / N, px / N); c.translate(N / 2, N / 2); c.fillStyle = hex; c.strokeStyle = "rgba(20,20,19,0.5)"; c.lineWidth = 3; c.lineJoin = "round"; const r = N * 0.16;
  c.beginPath();
  if (shape === "hex") { for (let k = 0; k < 6; k++) { const a = k / 6 * 6.283 + 0.52; c.lineTo(Math.cos(a) * r * 1.15, Math.sin(a) * r * 1.15); } c.closePath(); }
  else if (shape === "tri") { c.moveTo(0, -r * 1.35); c.lineTo(r * 1.2, r * 0.9); c.lineTo(0, r * 0.35); c.lineTo(-r * 1.2, r * 0.9); c.closePath(); }
  else if (shape === "oval") c.ellipse(0, 0, r * 1.45, r * 0.9, 0, 0, 7);
  else if (shape === "dia") { c.moveTo(0, -r * 1.3); c.lineTo(r * 0.9, 0); c.lineTo(0, r * 1.3); c.lineTo(-r * 0.9, 0); c.closePath(); }
  else if (shape === "fur") { for (let k = 0; k < 12; k++) { const a = k / 12 * 6.283, rr = k % 2 ? r * 0.8 : r * 1.35; c.lineTo(Math.cos(a) * rr, Math.sin(a) * rr); } c.closePath(); }
  else c.arc(0, 0, r * 0.95, 0, 7);
  c.fill(); c.stroke();
  SPR.set(key, s); return s;
}
const sizePx = (c) => 1.6 + (c[1] / 39) * 3.2;
const colorOf = (c) => COLORS[P[c[3]][1]] || "#c8c4b8";

// ---------- positions (deterministic in time, so scrubbing is exact)
let homeCache = new Map();
function homeOf(i, isl) {
  const hk = i * 8 + isl, hc = homeCache.get(hk); if (hc) return hc;
  const c = cr[i], sp = c[16];
  const a1 = h2(sp, isl * 31) * 6.283, r1 = Math.sqrt(h2(sp + 5, isl)) * 0.62;
  const a2 = hash(i * 7 + isl) * 6.283, r2 = Math.sqrt(hash(i * 13 + 3)) * 0.9;
  const b = blobs[isl];
  let x = Math.cos(a1) * r1 * 0.4 + Math.cos(a2) * r2 * 0.78, y = Math.sin(a1) * r1 * 0.4 + Math.sin(a2) * r2 * 0.78;
  const d = Math.hypot(x, y), lim = 0.84 * blobR(isl, Math.atan2(y, x)); if (d > lim) { x *= lim / d; y *= lim / d; }
  const out = [b.cx + x * b.R, b.cy + y * b.R]; homeCache.set(hk, out); return out;
}
let MOT, SPRI, BUR, SZ;
function prepCreatures() {
  MOT = new Float32Array(nC * 3); SPRI = new Array(nC); BUR = new Uint8Array(nC); SZ = new Float32Array(nC);
  for (let i = 0; i < nC; i++) {
    const c = cr[i], loc = P[c[5]][3];
    let amp = 3.2, sp = 0.9;
    if (/aquatic/.test(loc)) { amp = 7; sp = 0.6; } else if (/fly/.test(loc)) { amp = 10; sp = 1.4; } else if (/run/.test(loc)) { amp = 6; sp = 1.5; }
    else if (/burrow|crawl/.test(loc)) { amp = 1.8; sp = 0.5; }
    MOT[i * 3] = amp; MOT[i * 3 + 1] = sp; MOT[i * 3 + 2] = hash(i) * 100;
    SPRI[i] = [shapeOf(c), colorOf(c)]; BUR[i] = /burrow/.test(loc) ? 1 : 0; SZ[i] = sizePx(c);
  }
}
function motion(i) {
  const amp = MOT[i * 3] * S / 900, sp = MOT[i * 3 + 1], ph = MOT[i * 3 + 2];
  const T = clk * 1.3 * sp;
  return [amp * (Math.sin(T + ph) + 0.5 * Math.sin(2.3 * T + ph * 1.7)), amp * (Math.cos(1.3 * T + ph * 0.7) + 0.5 * Math.sin(1.9 * T + ph))];
}
function posAt(i, tt) {
  const c = cr[i]; let isl = c[9], from = -1, k0 = 0;
  for (const [g, to] of c[17]) { if (tt >= g) { from = isl; isl = to; k0 = g; } }
  if (from >= 0 && tt < k0 + 0.7) {
    const k = ease((tt - k0) / 0.7); const A = homeOf(i, from), B = homeOf(i, isl);
    const mx = (A[0] + B[0]) / 2 + (B[1] - A[1]) * 0.25, my = (A[1] + B[1]) / 2 - (B[0] - A[0]) * 0.25;
    return [(1 - k) * (1 - k) * A[0] + 2 * (1 - k) * k * mx + k * k * B[0], (1 - k) * (1 - k) * A[1] + 2 * (1 - k) * k * my + k * k * B[1], isl, true];
  }
  const h = homeOf(i, isl), m = motion(i); return [h[0] + m[0], h[1] + m[1], isl, false];
}

// ---------- frame
let rendered = [];
function frame() {
  const ctx = mctx; ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.globalAlpha = 1;
  ctx.drawImage(staticCanvas, 0, 0, MW, MH);
  const g = Math.min(Math.floor(t), G), fr = t - g, tt = t;
  rendered = [];
  const pinSp = pinned >= 0 ? cr[pinned][16] : -1;
  const sc0 = Math.max(0.75, S / 900);
  const drawOne = (i, alpha, scale) => {
    const c = cr[i]; const [x, y, , sea] = posAt(i, tt);
    const s = SZ[i] * scale * sc0, px = Math.max(4, Math.round(s * 5.2 * DPR)), d = px / DPR; const spr = sprite(SPRI[i][0], SPRI[i][1], px);
    let a = alpha; if (pinSp >= 0 && c[16] !== pinSp) a *= 0.3;
    if (BUR[i]) a *= 0.55 + 0.45 * Math.sin(tt * 3 + i);
    ctx.globalAlpha = a; ctx.drawImage(spr, Math.round((x - d / 2) * DPR) / DPR, Math.round((y - d / 2) * DPR) / DPR, d, d);
    if (sea) { ctx.globalAlpha = a * 0.25; ctx.drawImage(spr, x - s * 4, y - s * 4, s * 8, s * 8); }
    rendered.push(x, y, i);
  };
  for (const i of alive[g]) {
    const c = cr[i]; let sc = 1, al = 1;
    if (c[10] === g && g > 0) { const k = ease(fr / 0.35); sc = 0.2 + 0.8 * k; al = k; }
    drawOne(i, al, sc);
  }
  if (fr < 0.6) for (const i of diedAt[g] || []) {
    const c = cr[i]; const k = fr / 0.6; const [x, y] = posAt(i, tt);
    ctx.globalAlpha = (1 - k) * 0.85;
    if (c[12] === 1) {
      ctx.strokeStyle = RED; ctx.lineWidth = 0.9;
      if (c[13] >= 0 && fr < 0.3) { const [kx, ky] = posAt(c[13], tt); ctx.globalAlpha = (1 - k) * 0.45; ctx.beginPath(); ctx.moveTo(kx, ky); ctx.lineTo(x, y); ctx.stroke(); }
      ctx.beginPath(); ctx.arc(x, y, 2 + k * 8, 0, 7); ctx.stroke();
    } else if (c[12] !== 5) {
      ctx.strokeStyle = "rgba(20,20,19,0.3)"; ctx.lineWidth = 0.6; ctx.beginPath(); ctx.arc(x, y, 1 + k * 5, 0, 7); ctx.stroke();
    }
    if (pinSp < 0) drawOne(i, (1 - k) * 0.6, 1 - k * 0.6);
  }
  for (const e of events) {
    if (e.kind !== "ext") continue; const dt = t - e.g; if (dt < 0 || dt > 2.2) continue;
    const b = blobs[e.isl]; const k = dt / 2.2;
    for (let w = 0; w < 3; w++) { const kk = k - w * 0.12; if (kk <= 0) continue;
      ctx.globalAlpha = (1 - kk) * 0.5; ctx.strokeStyle = RED; ctx.lineWidth = 1.4 - w * 0.4;
      ctx.beginPath(); ctx.arc(b.cx, b.cy, b.R * (0.3 + kk * 1.6), 0, 7); ctx.stroke(); }
  }
  ctx.globalAlpha = 1;
  // island labels: name in ink beside a colour dot, population underneath
  const small = MW < 560;
  ISL.forEach((isl, k) => {
    const b = blobs[k]; const y = b.cy + b.R * 1.1 + 12;
    ctx.font = `600 ${small ? 10 : 11}px Inter`; ctx.letterSpacing = "1.2px"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    const name = isl.name.toUpperCase(), tw = ctx.measureText(name).width;
    ctx.fillStyle = isl.color; ctx.beginPath(); ctx.arc(b.cx - tw / 2 - 8, y, 3.5, 0, 7); ctx.fill();
    ctx.fillStyle = INK; ctx.fillText(name, b.cx, y);
    ctx.letterSpacing = "0px"; ctx.fillStyle = INK3; ctx.font = `400 ${small ? 9.5 : 10.5}px Inter`;
    ctx.fillText(`${D.pop[g * NI + k]} alive`, b.cx, y + 14);
  });
  ctx.textBaseline = "alphabetic";
  const hi = pinned >= 0 ? pinned : hover;
  if (hi >= 0 && cr[hi][10] <= t && (cr[hi][11] < 0 || cr[hi][11] > t - 0.6)) {
    const [x, y] = posAt(hi, t); ctx.strokeStyle = INK; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(x, y, 9, 0, 7); ctx.stroke();
    for (const p of [cr[hi][14], cr[hi][15]]) if (p >= 0 && cr[p][10] <= t && (cr[p][11] < 0 || cr[p][11] > t)) {
      const [px, py] = posAt(p, t); ctx.setLineDash([2, 3]); ctx.strokeStyle = "rgba(20,20,19,.55)"; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(px, py); ctx.stroke(); ctx.setLineDash([]);
    }
  }
}

// ---------- tree of life (radial: angle = lineage, radius = time); drawn into a cached canvas per generation
let tree, tctx, TW = 1, TH = 1, treeLayout, treeKey = "";
function sizeTree() { [TW, TH] = fit(tree); treeKey = ""; }
function buildTree() {
  const ok = new Set(D.species.filter((s) => s.peak >= 25).map((s) => s.id));
  const par = (s) => { let p = s.parent; while (p != null && !ok.has(p)) p = spById.get(p)?.parent ?? null; return p; };
  const kids = new Map(); const roots = Array.from({ length: NI }, () => []);
  for (const s of D.species) if (ok.has(s.id)) { const p = par(s); if (p == null) roots[s.isl].push(s); else { if (!kids.has(p)) kids.set(p, []); kids.get(p).push(s); } }
  const order = [];
  const visit = (s) => { order.push(s); (kids.get(s.id) || []).sort((a, b) => a.born - b.born).forEach(visit); };
  roots.forEach((rs) => { rs.sort((a, b) => b.peak - a.peak).forEach(visit); order.push(null, null, null); });
  const leafIdx = new Map(); order.forEach((s, k) => { if (s) leafIdx.set(s.id, k); });
  shownSp = order.filter(Boolean);
  treeLayout = { total: order.length, par, leafIdx };
  $("#i-spcount").textContent = `${shownSp.length} species reached 25+ members`;
  treeKey = "";
}
function drawTree() {
  const pinSp = pinned >= 0 ? cr[pinned][16] : -1;
  const key = `${Math.round(t * 4)}|${pinSp}|${TW}x${TH}`;
  if (key === treeKey) return; treeKey = key;
  const c = tctx; c.setTransform(DPR, 0, 0, DPR, 0, 0); c.clearRect(0, 0, TW, TH);
  const cx = TW / 2, cy = TH / 2, R0 = 16, R1 = Math.min(TW, TH) / 2 - 14;
  if (R1 <= R0 + 10) return;
  const rad = (g) => R0 + (R1 - R0) * Math.pow(g / G, 0.62);
  const ang = (s) => (treeLayout.leafIdx.get(s.id) / treeLayout.total) * Math.PI * 2 - Math.PI / 2;
  c.strokeStyle = "rgba(20,20,19,0.06)"; c.lineWidth = 1;
  for (let g = 20; g <= G; g += 20) { c.beginPath(); c.arc(cx, cy, rad(g), 0, 7); c.stroke(); }
  c.fillStyle = INK4; c.font = "9.5px Inter"; c.textAlign = "left";
  for (let g = 20; g <= G; g += 20) c.fillText(`${g}`, cx + 3, cy - rad(g) - 2);
  c.strokeStyle = "rgba(20,20,19,0.3)"; c.setLineDash([2, 4]); c.beginPath(); c.arc(cx, cy, rad(Math.min(t, G)), 0, 7); c.stroke(); c.setLineDash([]);
  const lineage = new Set(); if (pinSp >= 0) { let s = spById.get(pinSp); while (s) { lineage.add(s.id); s = spById.get(s.parent); } }
  c.lineCap = "round";
  for (const s of shownSp) {
    if (s.born > t) continue;
    const col = ISL[s.isl].color, a = ang(s), end = Math.min(s.ext ?? G, t);
    const hl = lineage.has(s.id); const dim = pinSp >= 0 && !hl ? 0.22 : 1;
    const p = treeLayout.par(s);
    if (p != null && spById.get(p) && treeLayout.leafIdx.has(p)) {
      const pa = ang(spById.get(p)), r = rad(s.born);
      c.strokeStyle = rgba(col, 0.4 * dim); c.lineWidth = 0.8; c.beginPath(); c.arc(cx, cy, r, Math.min(a, pa), Math.max(a, pa)); c.stroke();
    }
    const ca = Math.cos(a), sa = Math.sin(a);
    for (let g = Math.max(s.born, 1); g < end; g++) {
      const n = s.counts[g - 1] || 0; if (!n) continue;
      const w = 0.5 + Math.sqrt(n) * 0.26;
      c.strokeStyle = rgba(col, (hl ? 1 : 0.8) * dim); c.lineWidth = hl ? w + 1 : w;
      c.beginPath(); c.moveTo(cx + ca * rad(g), cy + sa * rad(g)); c.lineTo(cx + ca * rad(g + 1), cy + sa * rad(g + 1)); c.stroke();
    }
    if (s.ext && s.ext <= t) { const r = rad(s.ext); c.fillStyle = rgba(RED, 0.8 * dim); c.beginPath(); c.arc(cx + ca * r, cy + sa * r, 1.4, 0, 7); c.fill(); }
  }
  // labels: the largest living species per island at the current time
  const g = Math.min(Math.floor(t), G);
  c.font = "10.5px Inter"; c.textBaseline = "middle";
  const placed = [];
  for (let isl = 0; isl < NI; isl++) {
    let best = null, bn = 0;
    for (const s of shownSp) { if (s.born > t || (s.ext && s.ext <= t)) continue; const n = spIslCounts.get(s.id * 8 + isl)?.[g] || 0; if (n > bn) { bn = n; best = s; } }
    if (!best || g < 3 || !treeLayout.leafIdx.has(best.id)) continue;
    const a = ang(best), r = rad(Math.min(t, G)) + 6; const x = cx + Math.cos(a) * r; let y = clamp(cy + Math.sin(a) * r, 10, TH - 10);
    while (placed.some((q) => Math.abs(q - y) < 15)) y += 15;
    placed.push(y);
    c.fillStyle = ISL[isl].color; c.beginPath(); c.arc(cx + Math.cos(a) * (r - 6), cy + Math.sin(a) * (r - 6), 2.6, 0, 7); c.fill();
    const right = Math.cos(a) >= 0; c.textAlign = right ? "left" : "right";
    let label = best.name; const maxw = TW * 0.48;
    while (c.measureText(label).width > maxw && label.length > 8) label = label.slice(0, -2);
    if (label !== best.name) label = label.trimEnd() + "…";
    const tw = c.measureText(label).width + 8; const lx = right ? Math.min(x, TW - tw) : Math.max(x, tw);
    c.fillStyle = "rgba(255,255,255,0.92)"; c.fillRect(right ? lx : lx - tw, y - 8, tw, 16);
    c.fillStyle = INK2; c.fillText(label, lx + (right ? 4 : -4), y);
  }
  c.textBaseline = "alphabetic";
}

// ---------- adaptation cards (features chosen from the cross-run summary, so every run shows the same measured features)
const HL_OK = ["insul", "blubber", "feathers", "scales", "armor", "white", "sandy", "dark", "green", "big", "small", "aquatic", "fly", "burrow", "climb", "run", "noct", "water", "heat", "cold", "cave", "herb", "carn", "social"];
let cardFeats = [], founderF = [], cardEls = [];
function featAt(g, isl, f) { return g <= 0 ? founderF[isl][f] : D.stats[g - 1][isl].f[f]; }
function buildCards() {
  founderF = ISL.map((_, isl) => { const rows = cr.filter((c) => c[10] === 0 && c[9] === isl); const o = {};
    for (const f of D.meta.features) o[f] = rows.filter((c) => [1, 2, 3, 4, 5, 6, 7, 8].some((k) => P[c[k]][3].split(" ").includes(f))).length / Math.max(rows.length, 1); return o; });
  cardFeats = ISL.map((_, k) => {
    let list = summary ? summary.rank[k].filter((f) => HL_OK.includes(f)).slice(0, 3) : [];
    if (list.length < 3) list = HL_OK.map((f) => [featAt(G, k, f) - featAt(0, k, f), f]).sort((a, b) => b[0] - a[0]).slice(0, 3).map((x) => x[1]);
    return list;
  });
  const el = $("#i-cards"); el.innerHTML = "";
  cardEls = ISL.map((isl, k) => {
    const d = document.createElement("div"); d.className = "acard";
    d.innerHTML = `<div class="h"><i class="sw" style="background:${isl.color}"></i>${isl.name}</div>` +
      cardFeats[k].map((f) => `<div class="tr"><span class="nm">${FEAT_LABEL[f]}<small>from ${Math.round(featAt(0, k, f) * 100)}%</small></span><span class="bar"><i style="background:${isl.color}"></i></span><b>0%</b></div>`).join("");
    el.appendChild(d);
    return [...d.querySelectorAll(".tr")].map((r) => [r.querySelector("i"), r.querySelector("b")]);
  });
}
let lastCardG = -1;
function updateCards() {
  const g = Math.min(Math.floor(t), G); if (g === lastCardG) return; lastCardG = g;
  ISL.forEach((_, k) => cardFeats[k].forEach((f, j) => { const v = featAt(g, k, f); cardEls[k][j][0].style.width = `${v * 100}%`; cardEls[k][j][1].textContent = `${Math.round(v * 100)}%`; }));
}

// ---------- event lines under the map
let lastTickG = -1;
function updateTicker() {
  const g = Math.min(Math.floor(t), G); if (g === lastTickG) return; lastTickG = g;
  const ev = events.filter((e) => e.g <= g).slice(-2).reverse();
  $("#i-events").innerHTML = ev.length ? ev.map((e) => `<div><span class="g">Gen ${e.g}</span><i class="dot" style="background:${e.kind === "ext" ? RED : ISL[e.isl].color}"></i><span>${e.txt}</span></div>`).join("")
    : `<div><span class="g">Gen 0</span><span>Every island holds the same 300 random creatures.</span></div>`;
}

// ---------- tooltip / inspector for one creature
function lineageText(spId) {
  const names = []; let s = spById.get(spId), n = 0;
  while (s && n < 4) { names.push(`${s.name} <span class="m">(generation ${s.born})</span>`); s = spById.get(s.parent); n++; }
  return names.join("<br>↑ ");
}
function showTip(i, mx, my) {
  const tip = $("#i-tip"); if (i < 0) { tip.classList.remove("on"); return; }
  const c = cr[i], sp = spById.get(c[16]);
  const rows = [1, 2, 3, 4, 5, 6, 7, 8].map((k) => `<div class="row"><i>${SLOT_NAME[k - 1]}</i><span>${P[c[k]][0]}</span></div>`).join("");
  const fate = c[11] < 0 ? "alive at the end" : c[12] === 1 && c[13] >= 0 ? `eaten in generation ${c[11]} by a ${spById.get(cr[c[13]][16])?.name || "predator"}` : `${CAUSE[c[12]]} in generation ${c[11]}`;
  tip.innerHTML = `<div class="n">${sp ? sp.name : "unnamed lineage"}</div>${rows}<div class="meta">Born generation ${c[10]} on ${ISL[c[9]].name}; ${fate}.${sp ? "<br>Lineage: " + lineageText(sp.id) : ""}</div>${pinned >= 0 ? '<div class="m">Click again to release.</div>' : '<div class="m">Click to pin and see its family.</div>'}`;
  tip.classList.add("on");
  const r = map.getBoundingClientRect(), tw = Math.min(300, r.width - 16);
  tip.style.width = `${tw}px`;
  const left = mx + 16 + tw > r.width - 8 ? mx - tw - 16 : mx + 16;
  tip.style.left = `${clamp(left, 8, r.width - tw - 8)}px`; tip.style.top = `${clamp(my - 40, 8, Math.max(8, r.height - tip.offsetHeight - 8))}px`;
}
function nearest(e) {
  const r = map.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
  let best = -1, bd = 120;
  for (let k = 0; k < rendered.length; k += 3) { const d = (rendered[k] - x) ** 2 + (rendered[k + 1] - y) ** 2; if (d < bd) { bd = d; best = rendered[k + 2]; } }
  return [best, x, y];
}

// ---------- wide modes: convergence across runs, food web
let wide, wctx;
function drawWide() {
  const [w, h] = fit(wide); const c = wctx; c.setTransform(DPR, 0, 0, DPR, 0, 0); c.clearRect(0, 0, w, h);
  c.fillStyle = "#ffffff"; c.fillRect(0, 0, w, h);
  if (mode === "conv") drawConvergence(c, w, h); else drawFoodWeb(c, w, h);
}
function drawConvergence(c, w, h) {
  const S2 = summary; if (!S2) return; const ns = S2.seeds.length;
  const narrow = w < 700, cols = narrow ? 2 : NI, pad = 12, top = 8;
  const panels = []; S2.islands.forEach((isl, k) => S2.rank[k].filter((f) => HL_OK.includes(f)).slice(0, 3).forEach((f, j) => panels.push([k, j, S2.headline_all[k][f]])));
  // wide: 7 columns x 3 rows; narrow: two columns, one island per row pair
  const rows = narrow ? Math.ceil(panels.length / 2) : 3;
  const cw = (w - 24 - pad * (cols - 1)) / cols, ch = narrow ? 104 : (h - top - 28 - pad * (rows - 1)) / rows;
  panels.forEach(([k, j, feat], n) => {
    const col = narrow ? n % 2 : k, row = narrow ? Math.floor(n / 2) : j;
    const isl = { ...S2.islands[k], color: ISL_COLOR[S2.islands[k].key] };
    const x0 = 12 + col * (cw + pad), y0 = top + (narrow ? 0 : 20) + row * (ch + pad), fi = S2.features.indexOf(feat.f);
    if (!narrow && j === 0) { c.fillStyle = isl.color; c.beginPath(); c.arc(x0 + 4, top + 7, 3.5, 0, 7); c.fill(); c.fillStyle = INK; c.font = "600 12px Inter"; c.textAlign = "left"; c.fillText(isl.name, x0 + 12, top + 11); }
    c.fillStyle = "#faf9f5"; c.fillRect(x0, y0, cw, ch);
    c.strokeStyle = "#e8e6dc"; c.lineWidth = 1; c.strokeRect(x0 + 0.5, y0 + 0.5, cw - 1, ch - 1);
    const X = (g) => x0 + 6 + (g / S2.gens) * (cw - 12), Y = (v) => y0 + ch - 6 - v * (ch - 40);
    c.strokeStyle = "rgba(20,20,19,0.08)"; c.beginPath(); c.moveTo(X(0), Y(0.5)); c.lineTo(X(S2.gens), Y(0.5)); c.stroke();
    c.strokeStyle = "rgba(115,114,108,0.7)"; c.setLineDash([3, 3]); c.lineWidth = 1;
    S2.f.forEach((run) => { c.beginPath(); run.forEach((gen, g) => { let m = 0; gen.forEach((r, ii) => { if (ii !== k) m += r[fi]; }); m /= NI - 1; g ? c.lineTo(X(g), Y(m)) : c.moveTo(X(g), Y(m)); }); c.stroke(); });
    c.setLineDash([]);
    const sm = (run, g) => { let m = 0, q = 0; for (let z = Math.max(0, g - 2); z <= Math.min(run.length - 1, g + 2); z++) { m += run[z][k][fi]; q++; } return g === 0 ? run[0][k][fi] : m / q; };
    S2.f.forEach((run) => { c.strokeStyle = rgba(isl.color, 0.9); c.lineWidth = 1.6; c.beginPath(); run.forEach((gen, g) => { const v = sm(run, g); g ? c.lineTo(X(g), Y(v)) : c.moveTo(X(g), Y(v)); }); c.stroke(); });
    c.fillStyle = INK; c.font = "500 11.5px Inter"; c.textAlign = "left";
    c.fillText((narrow ? isl.name + ": " : "") + (FEAT_LABEL[feat.f] || feat.f), x0 + 7, y0 + 15);
    c.fillStyle = INK3; c.font = "10.5px Inter";
    c.fillText(`${Math.round(feat.a * 100)}% → ${Math.round(feat.b * 100)}%, up in ${feat.up} of ${ns}`, x0 + 7, y0 + 29);
  });
  $("#i-wnote").innerHTML = `Each panel is one feature's share of an island's population over ${S2.gens} generations. <b>Solid lines:</b> the ${ns} runs, each from a different random founding population. <b>Dashed lines:</b> the same feature averaged over the other six islands, as a control.`;
}
function drawFoodWeb(c, w, h) {
  const edges = (D.foodweb[String(webIsl)] || []).filter(([a, b]) => spById.has(a) && spById.has(b) && a !== b).slice(0, 60);
  const nodes = new Map(); for (const [a, b, n] of edges) for (const s of [a, b]) nodes.set(s, (nodes.get(s) || 0) + n);
  const ids = [...nodes.keys()].sort((a, b) => nodes.get(b) - nodes.get(a)).slice(0, w < 700 ? 10 : 16);
  const keep = new Set(ids); for (let k = edges.length - 1; k >= 0; k--) if (!keep.has(edges[k][0]) || !keep.has(edges[k][1])) edges.splice(k, 1);
  const lvl = new Map(ids.map((s) => [s, 0]));
  for (let it = 0; it < 12; it++) for (const s of ids) { const prey = edges.filter((e) => e[0] === s); if (prey.length) lvl.set(s, 1 + prey.reduce((m, e) => m + lvl.get(e[1]) * e[2], 0) / prey.reduce((m, e) => m + e[2], 0)); }
  const maxL = Math.max(1, ...lvl.values());
  const byRow = new Map(); ids.forEach((s) => { const r = Math.round((lvl.get(s) / maxL) * 3); if (!byRow.has(r)) byRow.set(r, []); byRow.get(r).push(s); });
  const pos = new Map();
  for (const [r, list] of byRow) { list.sort((a, b) => nodes.get(b) - nodes.get(a)); list.forEach((s, k) => pos.set(s, [70 + (w - 140) * (k + 0.5) / list.length, h - 50 - (r / 3) * (h - 160)])); }
  const mxn = Math.max(...edges.map((e) => e[2]), 1);
  for (const [a, b, n] of edges) {
    const [x1, y1] = pos.get(b), [x2, y2] = pos.get(a); c.strokeStyle = rgba(RED, 0.12 + 0.5 * n / mxn); c.lineWidth = 0.6 + 4 * n / mxn;
    c.beginPath(); c.moveTo(x1, y1);
    if (Math.abs(y1 - y2) < 2) { const lift = Math.min(90, Math.abs(x2 - x1) * 0.35); c.bezierCurveTo(x1, y1 - lift, x2, y2 - lift, x2, y2); }
    else c.bezierCurveTo(x1, (y1 + y2) / 2, x2, (y1 + y2) / 2, x2, y2);
    c.stroke();
  }
  let li = 0;
  for (const s of ids) {
    const flip = (li++ % 2) === 1;
    const sp = spById.get(s), [x, y] = pos.get(s), r = 4 + Math.sqrt(sp.peak) * 0.8; const col = COLORS[P[sp.g[2]][1]] || "#c8c4b8";
    c.fillStyle = col; c.strokeStyle = "rgba(20,20,19,.6)"; c.lineWidth = 1; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); c.stroke();
    c.fillStyle = INK2; c.font = "10.5px Inter"; c.textAlign = "center";
    const words = sp.name.split(" "); const half = Math.ceil(words.length / 2);
    const ly = flip ? y - r - 20 : y + r + 13;
    c.fillText(words.slice(0, half).join(" "), x, ly); c.fillText(words.slice(half).join(" "), x, ly + 12);
  }
  c.fillStyle = INK3; c.font = "10.5px Inter"; c.textAlign = "left";
  c.fillText("Top predators", 8, 18); c.fillText("Prey", 8, h - 10);
  $("#i-wnote").innerHTML = `Who eats whom on <b>${ISL[webIsl].name}</b>, run ${seed}. Each line is a predator-prey link that Jev judged possible and the simulation then played out; thicker lines mean more kills over all ${G} generations. Height is the level in the food chain. Dot colour is the species' colour.`;
}

// ---------- modes and controls
function setMode(m) {
  mode = m;
  $("#i-modes").querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.m === m));
  $("#fig-islands").dataset.mode = m;
  $("#i-webisl").hidden = m !== "web";
  pinned = -1; showTip(-1);
  resize();
}
function setPlaying(p) { playing = p; $("#i-play").innerHTML = p ? PAUSE : PLAY; $("#i-play").setAttribute("aria-label", p ? "Pause" : "Play"); }
const PLAY = '<svg viewBox="0 0 12 12"><path d="M2.5 1.2v9.6L10.6 6z" fill="currentColor"/></svg>';
const PAUSE = '<svg viewBox="0 0 12 12"><rect x="2" y="1.5" width="2.8" height="9" rx=".6" fill="currentColor"/><rect x="7.2" y="1.5" width="2.8" height="9" rx=".6" fill="currentColor"/></svg>';

function render() {
  if (!D || loading) return;
  if (mode === "map" && !staticCanvas) { if (visible()) resize(); return; }
  if (mode === "map") { frame(); drawTree(); }
  updateCards(); updateTicker();
  $("#i-gen").textContent = `Generation ${Math.min(Math.floor(t), G)} of ${G}`;
  if (document.activeElement !== $("#i-range")) $("#i-range").value = t;
}
function tick(ts) {
  const dt = lastTs ? Math.min((ts - lastTs) / 1000, 0.1) : 0; lastTs = ts;
  if (D && visible()) {
    clk += dt;
    if (playing) { t += dt * speed * 0.55; if (t >= G + 0.999) { t = G + 0.999; setPlaying(false); } }
    render();
  }
  requestAnimationFrame(tick);
}

async function init() {
  map = $("#i-map"); mctx = map.getContext("2d"); tree = $("#i-tree"); tctx = tree.getContext("2d"); wide = $("#i-wide"); wctx = wide.getContext("2d");
  map.addEventListener("mousemove", (e) => { const [b, x, y] = nearest(e); hover = b; if (pinned < 0) showTip(b, x, y); });
  map.addEventListener("mouseleave", () => { hover = -1; if (pinned < 0) showTip(-1); });
  map.addEventListener("click", (e) => { const [b, x, y] = nearest(e); hover = b; pinned = pinned === b ? -1 : b; showTip(pinned >= 0 ? pinned : -1, x, y); treeKey = ""; });
  $("#i-play").onclick = () => { if (!playing && t >= G) t = 0; setPlaying(!playing); };
  $("#i-speeds").querySelectorAll("button").forEach((b) => b.onclick = () => { speed = +b.dataset.s; $("#i-speeds").querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b)); });
  $("#i-range").oninput = (e) => { t = +e.target.value; };
  $("#i-modes").querySelectorAll("button").forEach((b) => b.onclick = () => setMode(b.dataset.m));
  try { seeds = (await (await fetch("../runs/index.json")).json()).seeds; } catch (e) {}
  try { summary = await (await fetch("../runs/summary.json")).json(); } catch (e) {}
  const ss = $("#i-seeds");
  ss.innerHTML = seeds.map((s) => `<button data-s="${s}" class="${s === seed ? "on" : ""}">Run ${s}</button>`).join("");
  ss.querySelectorAll("button").forEach((b) => b.onclick = async () => {
    seed = +b.dataset.s; ss.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
    pinned = -1; hover = -1; showTip(-1); lastTickG = -1; lastCardG = -1; await load(seed); t = 0; setPlaying(true);
  });
  const wi = $("#i-webisl");
  wi.innerHTML = ["tundra", "ocean", "rainforest", "grassland", "desert", "volcanic", "cave"].map((k, i) => `<button data-i="${i}" class="${i === webIsl ? "on" : ""}"><i class="sw" style="background:${ISL_COLOR[k]}"></i>${ISL_NAME[k]}</button>`).join("");
  wi.querySelectorAll("button").forEach((b) => b.onclick = () => { webIsl = +b.dataset.i; wi.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b)); drawWide(); });
  setPlaying(playing);
  await load(seed);
  if (Q.has("t")) t = +Q.get("t");
  if (Q.has("pin")) pinned = +Q.get("pin");
  window.addEventListener("resize", resize);
  window.__islandsReady = true;
  if (!RENDER) requestAnimationFrame(tick);
}

// headless rendering hooks (darwin/render_video.py)
const api = {
  init, resize, setMode,
  setT(x, c) { t = x; clk = c ?? x; render(); },
  caption(txt) { const el = $("#i-cap"); el.innerHTML = txt || ""; el.classList.toggle("on", !!txt); },
  pin(i) { pinned = i; hover = -1; treeKey = ""; if (i < 0) return showTip(-1); const [, , isl] = posAt(i, t); const b = blobs[isl]; render(); showTip(i, b.cx + b.R * 1.1, b.cy - b.R * 0.6); },
  async mode(m, isl) { if (isl != null) webIsl = isl; setMode(m || "map"); },
  onShow() { treeKey = ""; resize(); },
};
return api;
})();
