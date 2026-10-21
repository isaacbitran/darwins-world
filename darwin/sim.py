"""Darwin's World: evolution where every law of nature is a Jev judgment.

Per generation, on every island:
  1. Encounters: each meat-eater meets 2 random neighbors; Jev: "could A catch and eat B here?"
  2. Survival:   Jev: food here? / can it live and move in this habitat? / survive the harsh season?
  3. Breeding:   survivors refill the island (cap K, at most BIRTHS per survivor); child mixes two parents'
                 traits slot by slot; each slot mutates with prob MU to a random trait from the pool.
  4. Migration:  rare drift to a neighboring island.
"""
import argparse, gzip, json, math, os, random, sys, time, threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from traits import POOL, BY_SLOT, SLOTS, describe
from islands import ISLANDS, KEYS, NEIGHBORS
import jev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Every island answer Jev has given, committed (about 10 MB), so the five recorded runs replay exactly with no calls.
# One line per question: kind, island, genome(s), probability. Gzip members are appended, never rewritten.
CACHE_PATH = os.path.join(ROOT, "cache", "island_answers_mock.tsv.gz" if jev.MOCK else "island_answers.tsv.gz")
FEATURES = ["insul", "fur", "blubber", "feathers", "scales", "armor", "bare", "white", "sandy", "dark", "green", "bright", "sea",
            "big", "small", "aquatic", "fly", "burrow", "climb", "run", "noct", "day", "water", "heat", "cold", "cave",
            "herb", "carn", "filter", "scav", "omni", "social", "defense"]
HERB_DIETS = {i for i in BY_SLOT["diet"] if set(POOL[i]["tags"]) & {"herb", "filter"}}

class Cache:
    def __init__(self):
        self.d = {}
        if os.path.exists(CACHE_PATH):
            with gzip.open(CACHE_PATH, "rt") as f:
                for line in f:
                    p = line.rstrip("\n").split("\t")
                    self.d[(p[0], int(p[1]), *(tuple(map(int, g.split(","))) for g in p[2:-1]))] = float(p[-1])
        self.saved = set(self.d)
    def save(self):
        new = [k for k in self.d if k not in self.saved]
        if not new: return
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with gzip.open(CACHE_PATH, "at") as f:
            for k in new:
                f.write("\t".join([k[0], str(k[1]), *(",".join(map(str, g)) for g in k[2:]), repr(self.d[k])]) + "\n")
        self.saved.update(new)

def tags(g):
    t = set()
    for i in g: t.update(POOL[i]["tags"])
    return t

def run_questions(cache, jobs, tag):
    """jobs: dict key -> (island_idx, instructions). Fills cache[key] = noul. One pool of 16 workers across islands."""
    todo = [(k, v) for k, v in jobs.items() if k not in cache.d]
    by_isl = defaultdict(list)
    for k, (isl, ins) in todo: by_isl[isl].append((k, ins))
    calls = []
    for isl, items in by_isl.items():
        for i in range(0, len(items), 120):
            calls.append((isl, items[i:i + 120]))
    def do(c):
        isl, items = c
        qs = {f"q{j}": {"type": "noul", "instructions": ins} for j, (k, ins) in enumerate(items)}
        ans = jev._post(ISLANDS[isl]["env"], qs, tag)
        return [(k, float(ans[f"q{j}"]["noul"])) for j, (k, _) in enumerate(items)]
    with ThreadPoolExecutor(16) as ex:
        for res in ex.map(do, calls):
            for k, v in res: cache.d[k] = v
    return len(todo)

def q_food(g): return f"{describe(g)}\nCould this creature find enough food to live on this island?"
def q_hab(g): return f"{describe(g)}\nCould this creature live, move around and breathe in this habitat every day?"
def q_season(g, isl): return f"{describe(g)}\nWould this creature survive {ISLANDS[isl]['season']} on this island?"
def q_eat(a, b):
    return (f"First creature: {describe(a)}\nSecond creature: {describe(b)}\n"
            f"On this island, could the first creature catch and eat the second creature?")

def hamming(a, b): return sum(x != y for x, y in zip(a, b))

def simulate(seed, gens, K, n0, births=3, mu=0.06, migrate=0.004, gamma=1.5, eat_scale=0.7, floor=0.12, out=None, log=print):
    rng = random.Random(seed)
    cache = Cache()
    nI = len(ISLANDS)
    C = {}            # id -> creature dict
    species = {}      # id -> dict
    nid = [0]; nsp = [0]
    def new_species(parent, isl, gen, genome):
        s = nsp[0]; nsp[0] += 1
        species[s] = {"id": s, "parent": parent, "isl": isl, "born": gen, "type": genome, "ext": None, "counts": {}, "members": Counter()}
        return s
    def new_creature(g, isl, gen, p1, p2, sp):
        i = nid[0]; nid[0] += 1
        C[i] = {"i": i, "g": g, "isl": isl, "bi": isl, "b": gen, "d": None, "c": None, "k": None, "p": [p1, p2], "s": sp, "mv": [], "fit": None}
        return i
    # identical random founding population on every island
    founders = [tuple(rng.choice(BY_SLOT[s]) for s in SLOTS) for _ in range(n0)]
    for isl in range(nI):
        root = new_species(None, isl, 0, founders[0])
        for g in founders:
            new_creature(g, isl, 0, None, None, root)
    alive = {isl: [i for i, c in C.items() if c["isl"] == isl] for isl in range(nI)}
    # founding species: cluster founders greedily so the first tree level is meaningful
    for isl in range(nI):
        reps = []
        for i in alive[isl]:
            g = C[i]["g"]
            for (rg, sid) in reps:
                if hamming(g, rg) < 5: C[i]["s"] = sid; break
            else:
                sid = new_species(None, isl, 0, g) if reps else C[i]["s"]
                species[sid]["type"] = g
                reps.append((g, sid)); C[i]["s"] = sid
    stats, foodweb, events = [], defaultdict(Counter), []
    t0 = time.time()
    for gen in range(1, gens + 1):
        # ---- 1. encounters
        jobs, enc = {}, []
        for isl in range(nI):
            pop = alive[isl]
            if len(pop) < 2: continue
            for a in pop:
                if C[a]["g"][3] in HERB_DIETS: continue
                for _ in range(2):
                    b = rng.choice(pop)
                    if b == a: continue
                    key = ("eat", isl, C[a]["g"], C[b]["g"])
                    jobs[key] = (isl, q_eat(C[a]["g"], C[b]["g"])); enc.append((isl, a, b, key))
        n_eat = run_questions(cache, jobs, f"eat_s{seed}")
        rng.shuffle(enc)
        dead, fed = set(), set()
        for isl, a, b, key in enc:
            if a in dead or b in dead: continue
            p = cache.d[key]
            if rng.random() < eat_scale * p * p:
                dead.add(b); fed.add(a)
                C[b].update(d=gen, c="eaten", k=a)
                foodweb[isl][(C[a]["s"], C[b]["s"])] += 1
        # ---- 2. survival
        jobs = {}
        for isl in range(nI):
            for i in alive[isl]:
                if i in dead: continue
                g = C[i]["g"]
                jobs[("food", isl, g)] = (isl, q_food(g)); jobs[("hab", isl, g)] = (isl, q_hab(g)); jobs[("sea", isl, g)] = (isl, q_season(g, isl))
        n_surv = run_questions(cache, jobs, f"surv_s{seed}")
        for isl in range(nI):
            for i in alive[isl]:
                if i in dead: continue
                c = C[i]; g = c["g"]
                f = cache.d[("food", isl, g)]; h = cache.d[("hab", isl, g)]; w = cache.d[("sea", isl, g)]
                if i in fed: f = max(f, 0.9)
                fit = (f * h * w) ** (1 / 3)
                c["fit"] = fit
                if gen - c["b"] >= 5:
                    dead.add(i); c.update(d=gen, c="old age"); continue
                if rng.random() > floor + (1 - floor) * fit ** gamma:
                    worst = min((f, "starved"), (h, "habitat"), (w, "season"))[1]
                    dead.add(i); c.update(d=gen, c=worst)
        for isl in range(nI): alive[isl] = [i for i in alive[isl] if i not in dead]
        # ---- 3. breeding
        for isl in range(nI):
            pop = alive[isl]
            if not pop: continue
            nb = min(K - len(pop), births * len(pop))
            w = [max(C[i]["fit"] or 0.01, 0.01) ** 2 for i in pop]
            bysp = defaultdict(list)
            for i in pop: bysp[C[i]["s"]].append(i)
            kids = []
            for _ in range(max(nb, 0)):
                p1 = rng.choices(pop, w)[0]
                mates = bysp[C[p1]["s"]]
                p2 = rng.choice(mates) if (len(mates) > 1 and rng.random() < 0.8) else p1
                g = tuple((a if rng.random() < 0.5 else b) for a, b in zip(C[p1]["g"], C[p2]["g"]))
                g = tuple((rng.choice(BY_SLOT[SLOTS[s]]) if rng.random() < mu else x) for s, x in enumerate(g))
                sp = C[p1]["s"]
                if hamming(g, species[sp]["type"]) >= 3:
                    sp = new_species(sp, isl, gen, g)
                    bysp[sp] = []
                kids.append(new_creature(g, isl, gen, p1, p2, sp))
            alive[isl] = pop + kids
        # ---- 4. migration
        moves = []
        for isl in range(nI):
            for i in alive[isl]:
                t = tags(C[i]["g"])
                rate = migrate * (3 if t & {"aquatic", "fly"} else 1)
                if rng.random() < rate:
                    to = KEYS.index(rng.choice(NEIGHBORS[KEYS[isl]]))
                    moves.append((i, isl, to))
        for i, a, b in moves:
            alive[a].remove(i); alive[b].append(i); C[i]["mv"].append([gen, b]); C[i]["isl"] = b
            events.append({"t": "migrate", "gen": gen, "i": i, "from": a, "to": b})
        # ---- stats
        row = []
        for isl in range(nI):
            pop = alive[isl]; cnt = Counter(); slot = [Counter() for _ in SLOTS]
            for i in pop:
                g = C[i]["g"]
                for s, x in enumerate(g): slot[s][x] += 1
                cnt.update(tags(g))
            n = max(len(pop), 1)
            row.append({"n": len(pop), "f": {k: round(cnt[k] / n, 3) for k in FEATURES},
                        "top": [[x for x, _ in sc.most_common(3)] for sc in slot],
                        "topf": [[round(v / n, 3) for _, v in sc.most_common(3)] for sc in slot]})
            for i in pop:
                sp = species[C[i]["s"]]; sp["counts"][gen] = sp["counts"].get(gen, 0) + 1; sp["members"][C[i]["g"]] += 1
        stats.append(row)
        live_sp = {C[i]["s"] for isl in range(nI) for i in alive[isl]}
        for s in species.values():
            if s["ext"] is None and s["counts"] and s["id"] not in live_sp:
                s["ext"] = gen
        log(f"s{seed} gen {gen:3d} pop " + " ".join(f"{r['n']:4d}" for r in row) +
            f" | eaten {sum(1 for c in C.values() if c['d']==gen and c['c']=='eaten')} | new Q eat {n_eat} surv {n_surv} | species alive {len(live_sp)} | ${jev.total_spend():.3f} | {time.time()-t0:.0f}s")
        if gen % 10 == 0: cache.save()
    cache.save()
    return export(seed, gens, K, C, species, stats, foodweb, events, out)

def species_name(sp):
    g = sp["members"].most_common(1)[0][0] if sp["members"] else sp["type"]
    L = [POOL[i]["label"] for i in g]
    size = POOL[g[0]]
    parts = []
    if "big" in size["tags"] or "small" in size["tags"]: parts.append(L[0])
    parts += [L[2], L[1], L[3]]
    return " ".join(parts)

def export(seed, gens, K, C, species, stats, foodweb, events, out):
    sp_ok = {s["id"] for s in species.values() if sum(s["counts"].values()) >= 8}
    # keep tree connected: re-parent pruned species' children to the nearest kept ancestor
    def anc(s):
        while s is not None and s not in sp_ok: s = species[s]["parent"]
        return s
    sp_out = []
    for s in species.values():
        if s["id"] not in sp_ok: continue
        sp_out.append({"id": s["id"], "parent": anc(s["parent"]), "isl": s["isl"], "born": s["born"], "ext": s["ext"],
                       "name": species_name(s), "peak": max(s["counts"].values()),
                       "counts": [s["counts"].get(g, 0) for g in range(1, gens + 1)],
                       "g": list((s["members"].most_common(1)[0][0]) if s["members"] else s["type"])})
    cr = []
    for c in C.values():
        cr.append([c["i"], *c["g"], c["bi"], c["b"],
                   -1 if c["d"] is None else c["d"], {"eaten": 1, "starved": 2, "habitat": 3, "season": 4, "old age": 5}.get(c["c"], 0),
                   -1 if c["k"] is None else c["k"], -1 if c["p"][0] is None else c["p"][0], -1 if c["p"][1] is None else c["p"][1],
                   anc(c["s"]) if anc(c["s"]) is not None else -1, c["mv"]])
    fw = {str(isl): [[a, b, n] for (a, b), n in cnt.most_common(200)] for isl, cnt in foodweb.items()}
    data = {"meta": {"seed": seed, "gens": gens, "K": K, "model": "jev-1.13.0",
                     "islands": [{k: v for k, v in i.items()} for i in ISLANDS], "slots": SLOTS, "features": FEATURES,
                     "pool": [[t["phrase"], t["label"], t["slot"], " ".join(t["tags"])] for t in POOL]},
            "creatures": cr, "species": sp_out, "stats": stats, "foodweb": fw,
            "events": [e for e in events if e["t"] != "migrate"] , "migrations": [[e["gen"], e["i"], e["from"], e["to"]] for e in events if e["t"] == "migrate"]}
    if out:
        json.dump(data, open(out, "w"), separators=(",", ":"))
    return data

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--gens", type=int, default=20)
    ap.add_argument("--K", type=int, default=60); ap.add_argument("--n0", type=int, default=60)
    ap.add_argument("--out", default=None); ap.add_argument("--budget", type=float, default=30.0)
    a = ap.parse_args()
    assert jev.total_spend() < a.budget, "budget reached"
    simulate(a.seed, a.gens, a.K, a.n0, out=a.out or os.path.join(ROOT, "runs", f"seed{a.seed}.json"))
