"""The arms race's physics table: every Jev judgment the coevolution simulation uses, fetched once per world.

A prey animal is 2 phrases (how it escapes + what it does when caught), a predator is 2 phrases (how it hunts + its
weapon or sense). Each slot has 8 phrases, so there are 64 prey types and 64 predator types. Jev answers:

  hunt[i][j]   for every predator type i and prey type j (4,096 questions): does this predator usually catch and eat
               this prey in this world? Jev sees one predator and one prey, never a population.
  prey_ok[j]   for every prey type (64 questions):  could it find food and raise young in this world?
  pred_ok[i]   for every predator type (64 questions): could it live and raise young in this world, if prey is around?

The answers are written to runs/arms/physics_<world>.json and committed, so the simulation, every control and the
viewer run offline and for free. Usage:
  python darwin/arms_physics.py --world savanna          # fetch (about 4,200 questions; skips anything cached)
  JEV_MOCK=1 python darwin/arms_physics.py --world savanna --out /tmp/mock_physics.json
"""
import argparse, json, os, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
import jev

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARMS = os.path.join(ROOT, "runs", "arms")
# Spend guard for this repo's ledger: the arms-race work must not push the all-time ledger past this total (USD).
LEDGER_CAP = float(os.environ.get("JEV_LEDGER_CAP", "8.55"))

ESCAPE = [  # prey slot 1: how it avoids being caught      (short label, phrase)
    ("sprinter", "outruns pursuers in a long, fast sprint across open ground"),
    ("burrower", "escapes down into a narrow burrow deep underground"),
    ("tree-climber", "climbs to the thinnest top branches of tall trees"),
    ("camouflaged", "freezes motionless, camouflaged to look exactly like the ground around it"),
    ("herd", "lives in a large herd that keeps watch and stampedes together"),
    ("flier", "flies away in an instant on strong wings"),
    ("diver", "dives into deep water and stays under for many minutes"),
    ("night-hider", "comes out only on the darkest nights and hides all day"),
]
DEFENSE = [  # prey slot 2: what happens if a predator reaches it
    ("no defense", "has no other defense"),
    ("armored", "is covered in thick, hard armor plates"),
    ("quilled", "is covered in long, sharp quills"),
    ("poisonous", "has deadly poison in its skin and flesh"),
    ("sprayer", "sprays a blinding, foul-smelling liquid at attackers"),
    ("horned giant", "is very large and fights back with heavy horns and hooves"),
    ("tiny", "is tiny and slips through any small gap"),
    ("tail-dropper", "drops its tail as a decoy and escapes while the attacker is distracted"),
]
HUNT = [  # predator slot 1: how it hunts
    ("sprint-chaser", "chases prey down at very high speed over short distances"),
    ("endurance tracker", "follows prey patiently for hours until the prey is exhausted"),
    ("ambusher", "waits hidden in ambush and strikes in a split second"),
    ("digger", "digs prey out of burrows with powerful claws"),
    ("tree-hunter", "climbs trees and hunts among the branches"),
    ("aerial diver", "hunts from the air, diving on prey from high above"),
    ("swimmer", "swims fast and hunts underwater"),
    ("pack hunter", "hunts in a coordinated pack of a dozen"),
]
WEAPON = [  # predator slot 2: its weapon or sense
    ("keen nose", "an extremely keen sense of smell"),
    ("heat vision", "heat-sensing eyes that find prey in total darkness"),
    ("crushing jaws", "jaws strong enough to crack armor and bone"),
    ("venom", "a venomous bite that kills in seconds"),
    ("poison-proof", "a body immune to poisons and toxins"),
    ("thick hide", "thick leathery skin that quills and sprays cannot get through"),
    ("sharp eyes", "sharp eyes that pick out camouflaged animals"),
    ("huge body", "a huge body, larger than any prey on the island"),
]
NS = 8
PREY = [(a, b) for a in range(NS) for b in range(NS)]   # prey type j = a * 8 + b
PRED = [(a, b) for a in range(NS) for b in range(NS)]   # predator type i = a * 8 + b

def prey_text(j): a, b = PREY[j]; return f"it {ESCAPE[a][1]}, and it {DEFENSE[b][1]}"
def pred_text(i): a, b = PRED[i]; return f"it {HUNT[a][1]}, and it has {WEAPON[b][1]}"
def prey_label(j): a, b = PREY[j]; return f"{ESCAPE[a][0]}, {DEFENSE[b][0]}"
def pred_label(i): a, b = PRED[i]; return f"{HUNT[a][0]}, {WEAPON[b][0]}"

def q_hunt(i, j):
    return (f"Predator: {pred_text(i)}.\nPrey animal: {prey_text(j)}.\n"
            f"In this world, when this predator hunts this prey animal, does it usually catch and eat it?")
def q_prey_ok(j):
    return f"An animal: {prey_text(j)}.\nIn this world, could this animal find enough food and raise its young?"
def q_pred_ok(i):
    return (f"A predator: {pred_text(i)}.\nIn this world, could this predator live and raise its young, "
            f"if there were enough prey animals around?")

WORLDS = {
    "savanna": "A river valley on Earth: wide open grassland, scattered tall trees, a deep slow river, soft soil that is "
               "easy to dig, and warm days with dark, moonless nights.",
    "locked": "A tidally locked planet. One side always faces its red sun and is bright, hot rock; the other side is "
              "always dark and frozen. Life lives only in a narrow ring of permanent dusk between them, with a shallow "
              "warm sea, low fungus forests and loose gravel. There is never day or night, only the same dim red light.",
    "heavy": "A planet with three times Earth's gravity and a very thick, dense atmosphere. Everything is heavy: falls are "
             "deadly, trees are short and stubby, the ground is hard packed clay, and the air is so dense that it "
             "feels like wading through water. Lakes are shallow and warm.",
}

def path_for(world): return os.path.join(ARMS, f"physics_{world}.json")

def fetch(world, out=None):
    out = out or path_for(world)
    state = WORLDS[world]
    have = json.load(open(out)) if os.path.exists(out) else {}
    ans = have.get("answers", {})
    jobs = {}
    for i in range(64):
        for j in range(64):
            jobs[f"h{i}_{j}"] = q_hunt(i, j)
    for j in range(64): jobs[f"y{j}"] = q_prey_ok(j)
    for i in range(64): jobs[f"r{i}"] = q_pred_ok(i)
    todo = [(k, q) for k, q in jobs.items() if k not in ans]
    print(f"{world}: {len(todo)} of {len(jobs)} questions to ask")
    chunks = [todo[k:k + 120] for k in range(0, len(todo), 120)]
    def do(ch):
        if not jev.MOCK and jev.total_spend() > LEDGER_CAP:
            raise RuntimeError(f"ledger total passed the cap of USD {LEDGER_CAP}")
        qs = {f"q{n}": {"type": "noul", "instructions": q} for n, (_, q) in enumerate(ch)}
        a = jev._post(state, qs, f"arms_{world}")
        return [(k, round(float(a[f"q{n}"]["noul"]), 4)) for n, (k, _) in enumerate(ch)]
    try:
        for g in range(0, len(chunks), 8):  # 8 calls at a time, saved after each wave
            with ThreadPoolExecutor(8) as ex:
                for res in ex.map(do, chunks[g:g + 8]):
                    ans.update(res)
            save(world, state, ans, out)
            print(f"  {len(ans)}/{len(jobs)} answered, ledger total USD {jev.total_spend():.4f}")
    finally:
        save(world, state, ans, out)
    return ans

def save(world, state, ans, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    full = len(ans) == 64 * 64 + 128
    data = {"world": world, "state": state, "model": "jev-1.13.0", "mock": jev.MOCK, "complete": full,
            "escape": ESCAPE, "defense": DEFENSE, "hunt": HUNT, "weapon": WEAPON,
            "questions": {"hunt": q_hunt(0, 0), "prey_ok": q_prey_ok(0), "pred_ok": q_pred_ok(0)},
            "answers": ans}
    if full:
        data["hunt_p"] = [[ans[f"h{i}_{j}"] for j in range(64)] for i in range(64)]
        data["prey_ok"] = [ans[f"y{j}"] for j in range(64)]
        data["pred_ok"] = [ans[f"r{i}"] for i in range(64)]
    json.dump(data, open(out, "w"), separators=(",", ":"))

def load(world, path=None):
    d = json.load(open(path or path_for(world)))
    assert d["complete"], f"physics table for {world} is incomplete; run arms_physics.py --world {world}"
    return d

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="savanna", choices=list(WORLDS))
    ap.add_argument("--out", default=None)
    ap.add_argument("--probe", action="store_true", help="ask 120 questions only and print token cost")
    a = ap.parse_args()
    if a.probe:
        qs = {f"q{n}": {"type": "noul", "instructions": q_hunt(n % 64, (n * 7) % 64)} for n in range(120)}
        t0 = jev.total_spend(); r = jev._post(WORLDS[a.world], qs, f"arms_probe")
        print("USD for 120 questions:", round(jev.total_spend() - t0, 5), "tokens:", jev.STATS["tokens"])
        for n in range(6): print(round(r[f"q{n}"]["noul"], 3), pred_label(n % 64), "vs", prey_label((n * 7) % 64))
    else:
        fetch(a.world, a.out)
