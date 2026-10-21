"""Cross-seed measurement: feature frequencies per island per generation for every run, plus the headline table."""
import json, glob, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from traits import POOL
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sorted(glob.glob(os.path.join(ROOT, "runs", "seed*.json")), key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
runs = [json.load(open(p)) for p in files]
seeds = [r["meta"]["seed"] for r in runs]
FE = runs[0]["meta"]["features"]; ISL = runs[0]["meta"]["islands"]; NI = len(ISL); G = min(r["meta"]["gens"] for r in runs)

def founders(r):
    rows = [c for c in r["creatures"] if c[10] == 0 and c[9] == 0]
    out = []
    for f in FE:
        out.append(sum(1 for c in rows if any(f in POOL[t]["tags"] for t in c[1:9])) / len(rows))
    return out

F = []  # [seed][gen][isl][feat]
for r in runs:
    f0 = founders(r)
    series = [[f0[:] for _ in range(NI)]]
    for g in range(G):
        series.append([[r["stats"][g][k]["f"][f] for f in FE] for k in range(NI)])
    F.append(series)

def endv(run, k, fi): return sum(run[g][k][fi] for g in range(G - 4, G + 1)) / 5
headline, table, table_full = [], [], []
for k in range(NI):
    rows = []
    for fi, f in enumerate(FE):
        a = sum(run[0][k][fi] for run in F) / len(F); b = sum(endv(run, k, fi) for run in F) / len(F)
        ctrl = sum(endv(run, j, fi) for run in F for j in range(NI) if j != k) / (len(F) * (NI - 1))
        up = sum(1 for run in F if endv(run, k, fi) - run[0][k][fi] > 0.2)
        rows.append({"f": f, "a": round(a, 3), "b": round(b, 3), "ctrl": round(ctrl, 3), "up": up, "rise": b - a})
    rows.sort(key=lambda x: (-(x["up"]), -(x["b"] - x["ctrl"])))
    headline.append([{k2: v for k2, v in x.items() if k2 != "rise"} for x in rows[:3]])
    table.append((ISL[k]["name"], rows[:6])); table_full.append((ISL[k]["name"], rows))

def composite(run_data, k, need):
    rows = [c for c in run_data["creatures"] if c[11] < 0 and (c[17][-1][1] if c[17] else c[9]) == k]
    hit = sum(1 for c in rows if all(any(n in POOL[t]["tags"] for t in c[1:9]) for n in need))
    return hit / max(len(rows), 1)

polar = [composite(r, 0, ["insul", "big"]) for r in runs]
note = (f"Each panel: one feature's share of the island's population over {G} generations. Solid lines: the {len(runs)} runs (each from a "
        f"different random founding population). Dashed lines: the same feature averaged over the other six islands, as a control.")
json.dump({"seeds": seeds, "gens": G, "features": FE, "islands": [{"name": i["name"], "key": i["key"], "color": i["color"]} for i in ISL],
           "f": [[[[round(v, 3) for v in isl] for isl in gen] for gen in run] for run in F], "headline": headline, "note": note,
           "polar": polar, "rank": [[x["f"] for x in rows] for _, rows in table_full],
           "headline_all": [{x["f"]: {k2: v for k2, v in x.items() if k2 != "rise"} for x in rows} for _, rows in table_full]}, open(os.path.join(ROOT, "runs", "summary.json"), "w"), separators=(",", ":"))
json.dump({"seeds": seeds}, open(os.path.join(ROOT, "runs", "index.json"), "w"))
print(f"{len(runs)} runs, {G} generations")
for name, rows in table:
    print(f"{name:<13}" + "  ".join(f"{x['f']} {x['a']*100:.0f}->{x['b']*100:.0f}% (others {x['ctrl']*100:.0f}%, {x['up']}/{len(runs)})" for x in rows[:4]))
print("Frostholm survivors with an insulating coat AND a large body, per run:", [f"{p*100:.0f}%" for p in polar])
