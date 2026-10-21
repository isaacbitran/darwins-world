"""Print per-island feature frequencies (first vs last generation) and dominant traits for one or more runs."""
import json, sys, os
EXPECT = {"tundra": ["insul", "white", "big", "cold"], "ocean": ["aquatic", "sea", "carn", "filter"],
          "rainforest": ["climb", "green", "herb"], "grassland": ["run", "social", "herb"],
          "desert": ["water", "noct", "burrow", "sandy", "heat"], "volcanic": ["heat", "armor", "dark"],
          "cave": ["cave", "noct"]}
for path in sys.argv[1:]:
    d = json.load(open(path)); st = d["stats"]; pool = d["meta"]["pool"]
    print(f"== {os.path.basename(path)} gens {len(st)}")
    for k, isl in enumerate(d["meta"]["islands"]):
        a, b = st[0][k]["f"], st[-1][k]["f"]
        feats = EXPECT[isl["key"]]
        line = "  ".join(f"{f} {a[f]*100:.0f}->{b[f]*100:.0f}" for f in feats)
        top = [f"{pool[t[0]][1]}({p[0]*100:.0f}%)" for t, p in zip(st[-1][k]["top"], st[-1][k]["topf"]) if t]
        print(f"{isl['key']:<10} n={st[-1][k]['n']:4d} | {line}\n           {' '.join(top)}")
