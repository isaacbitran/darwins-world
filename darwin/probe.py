"""Probe Jev's signal: do adapted creatures score higher on their island than random ones?"""
import random, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from traits import POOL, BY_SLOT, SLOTS, describe
from islands import ISLANDS
import jev

def find(slot, sub):
    return next(i for i in BY_SLOT[slot] if sub in POOL[i]["phrase"])

HAND = {
 "polar": [("size","bear"),("covering","thick, dense"),("color","pure snow"),("diet","seals"),("locomotion","snowshoe"),("activity","year-round"),("behavior","deep den"),("physiology","fat to survive")],
 "camel": [("size","goat"),("covering","sun-colored" if False else "shades the skin"),("color","pale sandy"),("diet","cactus"),("locomotion","stout"),("activity","only at night"),("behavior","shelters under rocks"),("physiology","almost never")],
 "fish":  [("size","seal"),("covering","smooth glossy"),("color","countershaded" if False else "dark blue on top"),("diet","eats fish"),("locomotion","fins and a tail"),("activity","year-round"),("behavior","underwater"),("physiology","gills")],
 "cavefish": [("size","frog"),("covering","translucent"),("color","pale ghostly"),("diet","fungi"),("locomotion","suction"),("activity","total darkness"),("behavior","deep caves"),("physiology","completely blind")],
 "monkey": [("size","cat"),("covering","short sleek"),("color","olive"),("diet","fruit and nuts"),("locomotion","swings"),("activity","during the day"),("behavior","rarely touches"),("physiology","thirsty" if False else "several times")],
}
rng = random.Random(1)
crit = {k: tuple(find(s, sub) for s, sub in v) for k, v in HAND.items()}
for n in range(30):
    crit[f"r{n}"] = tuple(rng.choice(BY_SLOT[s]) for s in SLOTS)
for isl in ISLANDS:
    qs = {}
    for k, g in crit.items():
        d = describe(g)
        qs[f"{k}|food"] = {"type": "noul", "instructions": f"{d}\nCould this creature find enough food to live on this island?"}
        qs[f"{k}|hab"] = {"type": "noul", "instructions": f"{d}\nCould this creature live, move around and breathe in this habitat every day?"}
        qs[f"{k}|sea"] = {"type": "noul", "instructions": f"{d}\nWould this creature survive {isl['season']} on this island?"}
    ans = jev.ask_many(qs, state=isl["env"], tag="probe")
    row = []
    for k in HAND:
        row.append(f"{k}:" + "/".join(f"{ans[f'{k}|{q}']['noul']:.2f}" for q in ("food", "hab", "sea")))
    rnd = [ans[f"r{n}|{q}"]["noul"] for n in range(30) for q in ("food", "hab", "sea")]
    import statistics
    print(isl["key"].ljust(10), " ".join(row), f"| random mean {statistics.mean(rnd):.2f} sd {statistics.pstdev(rnd):.2f}")
print("spend", round(jev.total_spend(), 4))
