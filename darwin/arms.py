"""Coevolution of predators and prey whose physics is a table of Jev judgments (darwin/arms_physics.py).

One world, two populations of fixed size. Every generation:
  1. Hunting:  each predator makes HUNTS attempts on prey drawn at random; an attempt by predator type i on prey type j
               kills with probability hunt_p[i][j] (Jev's answer).
  2. Prey:     survivors breed; parents are drawn in proportion to prey_ok^2 (Jev: can it find food and raise young?).
  3. Predators: parents are drawn in proportion to (kills + 0.25) * pred_ok^2.
  (A second, "predation-only" setting sets the exponent to 0 and HUNTS to 15, so viability no longer selects.)
  4. Mutation: each of a child's 2 phrases switches to a random phrase of the same slot with probability MU.

Nothing in this file knows what any phrase means. The physics table is the only input, so the same code runs on the
Jev table and on the control tables (shuffled, additive-only, frozen predators).

  python darwin/arms.py --world savanna --seeds 1-5          # all runs and controls -> runs/arms/<world>.json
"""
import argparse, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import arms_physics as P

N_PREY, N_PRED, HUNTS, MU, GENS, VIAB = 1000, 200, 5, 0.01, 600, 2.0

def simulate(hunt, prey_ok, pred_ok, seed, gens=GENS, freeze_pred=False, n_prey=N_PREY, n_pred=N_PRED, hunts=HUNTS, viab=VIAB):
    """viab is the exponent on prey_ok and pred_ok in the breeding weights (0 switches viability selection off, so
    only predation selects prey). hunts is the number of attempts each predator makes per generation."""
    rng = random.Random(seed)
    T = 64
    prey = [rng.randrange(T) for _ in range(n_prey)]
    pred = [rng.randrange(T) for _ in range(n_pred)]
    fy, fr, kills_t = [], [], []
    def mutate(t):
        a, b = divmod(t, 8)
        if rng.random() < MU: a = rng.randrange(8)
        if rng.random() < MU: b = rng.randrange(8)
        return a * 8 + b
    def counts(pop):
        c = [0] * T
        for t in pop: c[t] += 1
        return c
    fy.append(counts(prey)); fr.append(counts(pred))
    for g in range(gens):
        dead = [False] * n_prey
        kills = [0] * n_pred
        for k in range(n_pred):
            i = pred[k]
            for _ in range(hunts):
                v = rng.randrange(n_prey)
                if not dead[v] and rng.random() < hunt[i][prey[v]]:
                    dead[v] = True; kills[k] += 1
        surv = [prey[v] for v in range(n_prey) if not dead[v]] or prey
        w = [prey_ok[t] ** viab + 1e-6 for t in surv]
        prey = [mutate(t) for t in rng.choices(surv, w, k=n_prey)]
        if not freeze_pred:
            w = [(kills[k] + 0.25) * pred_ok[pred[k]] ** viab + 1e-6 for k in range(n_pred)]
            pred = [mutate(t) for t in rng.choices(pred, w, k=n_pred)]
        else:
            pred = [rng.randrange(T) for _ in range(n_pred)]  # predators stay a uniform random mix
        kills_t.append(sum(kills) / n_prey)
        fy.append(counts(prey)); fr.append(counts(pred))
    return {"prey": fy, "pred": fr, "kill_rate": kills_t}

# ---------- control physics tables
def logit(p): p = min(max(p, 1e-4), 1 - 1e-4); return math.log(p / (1 - p))
def sig(x): return 1 / (1 + math.exp(-x))

def additive_fit(hunt):
    """Best fit logit(p_ij) = mu + a_i + b_j (row and column means). Returns the fitted table and R^2 in logit space.
    An additive table is what kill odds would look like if they came from two separate per-animal questions
    (how dangerous is this predator? how vulnerable is this prey?) with no predator-prey interaction."""
    L = [[logit(x) for x in row] for row in hunt]
    n = len(L); m = len(L[0])
    mu = sum(map(sum, L)) / (n * m)
    a = [sum(r) / m - mu for r in L]
    b = [sum(L[i][j] for i in range(n)) / n - mu for j in range(m)]
    F = [[mu + a[i] + b[j] for j in range(m)] for i in range(n)]
    ss_tot = sum((L[i][j] - mu) ** 2 for i in range(n) for j in range(m))
    ss_res = sum((L[i][j] - F[i][j]) ** 2 for i in range(n) for j in range(m))
    return [[sig(x) for x in row] for row in F], 1 - ss_res / ss_tot

def shuffled(hunt, seed):
    rng = random.Random(1000 + seed)
    flat = [x for row in hunt for x in row]; rng.shuffle(flat)
    return [flat[i * 64:(i + 1) * 64] for i in range(64)]

# ---------- measurements
def freqs(c): s = sum(c) or 1; return [x / s for x in c]

def dominant_runs(series, burn=100, min_len=10):
    """Sequence of dominant types after burn-in, merging spells shorter than min_len generations."""
    dom = [max(range(64), key=lambda t: c[t]) for c in series[burn:]]
    spells = []
    for g, t in enumerate(dom):
        if spells and spells[-1][0] == t: spells[-1][2] = g + burn
        else: spells.append([t, g + burn, g + burn])
    out = []
    for s in spells:
        if s[2] - s[1] + 1 < min_len: continue
        if out and out[-1][0] == s[0]: out[-1][2] = s[2]
        else: out.append(s)
    return out

def motion(series, burn=100, lag=10):
    """Mean total-variation distance between the type distribution at t and t+lag after burn-in (0 = frozen, 1 = total turnover)."""
    f = [freqs(c) for c in series]
    d = [0.5 * sum(abs(x - y) for x, y in zip(f[t], f[t + lag])) for t in range(burn, len(f) - lag)]
    return sum(d) / len(d)

def time_shift(run, hunt, taus=range(-40, 41, 4), burn=100):
    """Kill probability of predators from generation t+tau against prey from generation t, averaged over t."""
    fy = [freqs(c) for c in run["prey"]]; fr = [freqs(c) for c in run["pred"]]
    G = len(fy); out = []
    burn = min(burn, G // 4)  # short test runs (--gens 150) still get a measurement
    assert G - 40 > burn + 40, "time_shift needs at least 120 generations"
    nzy = [[j for j in range(64) if fy[t][j] > 0] for t in range(G)]
    nzr = [[i for i in range(64) if fr[t][i] > 0] for t in range(G)]
    for tau in taus:
        vals = []
        for t in range(burn + 40, G - 40, 2):
            s = t + tau
            vals.append(sum(fr[s][i] * fy[t][j] * hunt[i][j] for i in nzr[s] for j in nzy[t]))
        out.append([tau, sum(vals) / len(vals)])
    return out

def best_response_cycle(hunt, prey_ok, pred_ok, viab=VIAB):
    """Follow best responses in the table: the prey type safest from predator i (weighted by prey_ok), then the predator
    type best at catching that prey (weighted by pred_ok), and so on, until a type repeats."""
    def prey_br(i): return max(range(64), key=lambda j: (1 - hunt[i][j]) * prey_ok[j] ** viab)
    def pred_br(j): return max(range(64), key=lambda i: hunt[i][j] * pred_ok[i] ** viab)
    i = max(range(64), key=lambda i: sum(hunt[i]) * pred_ok[i] ** viab)
    seen, chain = {}, []
    while ("r", i) not in seen:
        seen[("r", i)] = len(chain); chain.append(("pred", i))
        j = prey_br(i); chain.append(("prey", j)); i = pred_br(j)
    return chain[seen[("r", i)]:]

def single_question_optimum(hunt, prey_ok, viab=VIAB):
    """The prey type a fixed fitness function would pick: safest on average against all 64 predator types, times
    prey_ok^viab. If evolution only ever finds this type, the predators' evolution added nothing."""
    return max(range(64), key=lambda j: (1 - sum(hunt[i][j] for i in range(64)) / 64) * prey_ok[j] ** viab)

def single_question_predator(hunt, pred_ok, viab=VIAB):
    """The predator type that is best on average against all 64 prey types, times pred_ok^viab."""
    return max(range(64), key=lambda i: sum(hunt[i]) / 64 * pred_ok[i] ** viab)

def dominant(c): return max(range(64), key=lambda t: c[t])

def summarize_run(run, hunt):
    sp = dominant_runs(run["prey"]); sr = dominant_runs(run["pred"])
    G = len(run["prey"])
    return {"prey_spells": sp, "pred_spells": sr, "prey_turnovers": max(len(sp) - 1, 0), "pred_turnovers": max(len(sr) - 1, 0),
            "prey_motion": round(motion(run["prey"]), 4), "pred_motion": round(motion(run["pred"]), 4),
            "end_top_prey_share": round(max(freqs(run["prey"][-1])), 3),
            "end_prey": dominant(run["prey"][-1]), "end_pred": dominant(run["pred"][-1]),
            "mean_kill_rate": round(sum(run["kill_rate"][100:]) / (G - 101), 4)}

def slot_series(series, slot):
    """Share of each of the 8 phrases in one slot (0 = first slot, 1 = second) per generation."""
    out = []
    for c in series:
        s = sum(c) or 1; v = [0] * 8
        for t, n in enumerate(c): v[t // 8 if slot == 0 else t % 8] += n
        out.append([round(x / s, 4) for x in v])
    return out

def parse_seeds(s):
    if "-" in s: a, b = s.split("-"); return list(range(int(a), int(b) + 1))
    return [int(x) for x in s.split(",")]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="savanna"); ap.add_argument("--seeds", default="1-5")
    ap.add_argument("--gens", type=int, default=GENS); ap.add_argument("--physics", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-sensitivity", action="store_true", help="skip the predation-only setting")
    a = ap.parse_args()
    phy = P.load(a.world, a.physics)
    hunt, yok, rok = phy["hunt_p"], phy["prey_ok"], phy["pred_ok"]
    add, r2 = additive_fit(hunt)
    seeds = parse_seeds(a.seeds)
    def conditions(**kw):
        return {
            "jev": lambda s: simulate(hunt, yok, rok, s, a.gens, **kw),
            "frozen_predators": lambda s: simulate(hunt, yok, rok, s, a.gens, freeze_pred=True, **kw),
            "additive": lambda s: simulate(add, yok, rok, s, a.gens, **kw),
            "shuffled": lambda s: simulate(shuffled(hunt, s), yok, rok, s, a.gens, **kw),
        }
    res = {"world": a.world, "state": phy["state"], "mock": phy.get("mock", False), "seeds": seeds, "gens": a.gens,
           "params": {"n_prey": N_PREY, "n_pred": N_PRED, "hunts": HUNTS, "mu": MU},
           "labels": {"escape": [x[0] for x in P.ESCAPE], "defense": [x[0] for x in P.DEFENSE],
                      "hunt": [x[0] for x in P.HUNT], "weapon": [x[0] for x in P.WEAPON]},
           "phrases": {"escape": [x[1] for x in P.ESCAPE], "defense": [x[1] for x in P.DEFENSE],
                       "hunt": [x[1] for x in P.HUNT], "weapon": [x[1] for x in P.WEAPON]},
           "hunt_p": hunt, "prey_ok": yok, "pred_ok": rok,
           "additive_r2": round(r2, 4),
           "single_question_prey": single_question_optimum(hunt, yok),
           "single_question_pred": single_question_predator(hunt, rok),
           "most_viable_prey": max(range(64), key=lambda j: yok[j]),
           "prey_ok_rank": sorted(range(64), key=lambda j: -yok[j]),
           "best_response_cycle": best_response_cycle(hunt, yok, rok),
           "conditions": {}, "runs": {}}
    for name, fn in conditions().items():
        rows = []
        for s in seeds:
            run = fn(s)
            th = hunt if name != "additive" else add
            if name == "shuffled": th = shuffled(hunt, s)
            sm = summarize_run(run, th)
            sm["seed"] = s
            sm["time_shift"] = time_shift(run, th)
            if name == "jev":
                sq = res["single_question_prey"]
                sm["share_gens_single_question_dominant"] = round(
                    sum(1 for c in run["prey"][100:] if max(range(64), key=lambda t: c[t]) == sq) / (len(run["prey"]) - 100), 3)
                res["runs"][str(s)] = {"prey": run["prey"], "pred": run["pred"], "kill_rate": [round(x, 4) for x in run["kill_rate"]]}
            if name != "jev" and s == seeds[0]:
                res["runs"][f"{name}_{s}"] = {"prey": run["prey"], "pred": run["pred"],
                                              "kill_rate": [round(x, 4) for x in run["kill_rate"]]}
            rows.append(sm)
            print(f"{a.world} {name:17s} seed {s}: prey turnovers {sm['prey_turnovers']:3d}  pred turnovers {sm['pred_turnovers']:3d}"
                  f"  prey motion {sm['prey_motion']:.3f}  end top prey share {sm['end_top_prey_share']:.2f}")
        res["conditions"][name] = rows
    if not a.no_sensitivity:  # predation-only setting: viability does not select, predators hunt 3 times as often
        kw = {"viab": 0.0, "hunts": 15}
        sens = {"params": kw, "single_question_prey": single_question_optimum(hunt, yok, 0.0),
                "best_response_cycle": best_response_cycle(hunt, yok, rok, 0.0), "conditions": {}}
        for name, fn in conditions(**kw).items():
            rows = []
            for s in seeds:
                run = fn(s)
                th = add if name == "additive" else (shuffled(hunt, s) if name == "shuffled" else hunt)
                sm = summarize_run(run, th); sm["seed"] = s
                for k in ("prey_spells", "pred_spells"): sm.pop(k)
                sm["time_shift"] = time_shift(run, th)
                if name == "jev":
                    sq = sens["single_question_prey"]
                    sm["share_gens_single_question_dominant"] = round(
                        sum(1 for c in run["prey"][100:] if dominant(c) == sq) / (len(run["prey"]) - 100), 3)
                    res["runs"][f"po{s}"] = {"prey": run["prey"], "pred": run["pred"],
                                             "kill_rate": [round(x, 4) for x in run["kill_rate"]]}
                rows.append(sm)
                print(f"{a.world} predation-only {name:17s} seed {s}: prey turnovers {sm['prey_turnovers']:3d}"
                      f"  prey motion {sm['prey_motion']:.3f}  end top prey share {sm['end_top_prey_share']:.2f}")
            sens["conditions"][name] = rows
        res["predation_only"] = sens
    out = a.out or os.path.join(P.ARMS, f"{a.world}.json")
    json.dump(res, open(out, "w"), separators=(",", ":"))
    print("additive R^2 (logit):", res["additive_r2"], "| wrote", out)

if __name__ == "__main__":
    main()
