"""Summarize the arms-race runs: reads runs/arms/<world>.json (written by darwin/arms.py) and writes runs/arms/index.json,
the file the viewer loads first and the source of every number in the README's arms-race section.

  python darwin/arms_index.py            # prints the summary table too
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import arms_physics as P

NAMES = {"savanna": "Earth river valley", "locked": "Tidally locked planet", "heavy": "3x gravity planet"}
COND = ["jev", "additive", "shuffled", "frozen_predators"]

def ts_gap(row, tau=20):
    """Kill probability of predators from t+tau minus predators from t-tau, against prey from t (percentage points)."""
    d = dict((t, v) for t, v in row["time_shift"])
    return round(100 * (d[tau] - d[-tau]), 3)

def setting(block, ok_rank):
    out = {}
    for c in COND:
        rows = block["conditions"][c]
        out[c] = {"seeds": [r["seed"] for r in rows],
                  "prey_turnovers": [r["prey_turnovers"] for r in rows],
                  "pred_turnovers": [r["pred_turnovers"] for r in rows],
                  "prey_motion": [r["prey_motion"] for r in rows],
                  "end_top_prey_share": [r["end_top_prey_share"] for r in rows],
                  "time_shift_gap_pp": [ts_gap(r) for r in rows],
                  "end_prey": [P.prey_label(r["end_prey"]) for r in rows],
                  "end_pred": [P.pred_label(r["end_pred"]) for r in rows],
                  "end_prey_viability_rank": [ok_rank.index(r["end_prey"]) + 1 for r in rows]}
        if c == "jev":
            out[c]["share_gens_single_question_dominant"] = [r["share_gens_single_question_dominant"] for r in rows]
    return out

def main():
    worlds = []
    for w in ["savanna", "locked", "heavy"]:
        f = os.path.join(P.ARMS, f"{w}.json")
        if not os.path.exists(f): continue
        d = json.load(open(f))
        rank = d["prey_ok_rank"]
        worlds.append({
            "key": w, "name": NAMES[w], "state": d["state"], "mock": d["mock"], "gens": d["gens"],
            "additive_r2": d["additive_r2"],
            "most_viable_prey": P.prey_label(d["most_viable_prey"]),
            "default": {"params": {"viability_exponent": 2, "hunts": d["params"]["hunts"]},
                        "single_question_prey": P.prey_label(d["single_question_prey"]),
                        "conditions": setting(d, rank)},
            "predation_only": {"params": {"viability_exponent": 0, "hunts": 15},
                               "single_question_prey": P.prey_label(d["predation_only"]["single_question_prey"]),
                               "conditions": setting(d["predation_only"], rank)},
        })
    idx = {"worlds": worlds, "start": {"world": "locked", "rules": "po", "seed": "1"},
           "jev_questions_per_world": 64 * 64 + 128}
    json.dump(idx, open(os.path.join(P.ARMS, "index.json"), "w"), indent=1)
    for W in worlds:
        print(f"\n{W['name']}  (additive fit R^2 = {W['additive_r2']:.3f}, logit scale)")
        for key in ("default", "predation_only"):
            print(f"  {key}")
            for c, r in W[key]["conditions"].items():
                print(f"    {c:17s} prey switches {r['prey_turnovers']}  motion {[round(x, 3) for x in r['prey_motion']]}"
                      f"  time-shift gap pp {r['time_shift_gap_pp']}")
            print(f"    end prey (jev): {W[key]['conditions']['jev']['end_prey']}  viability rank {W[key]['conditions']['jev']['end_prey_viability_rank']}")

if __name__ == "__main__":
    main()
