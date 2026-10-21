"""Batched, concurrent Jev client with a persistent spend ledger. Key read from the repo .env at runtime; never printed."""
import json, os, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.environ.get("JEV_LEDGER") or os.path.join(os.path.dirname(HERE), "ledger.jsonl")
PRICE = 0.042 / 1e6  # USD per input token
_lock = threading.Lock()
_KEY = None

def _key():
    global _KEY
    if _KEY: return _KEY
    k = os.environ.get("TYPESAFE_API_KEY")
    if not k:
        with open(os.path.join(os.path.dirname(HERE), ".env")) as f:
            for line in f:
                if line.startswith("TYPESAFE_API_KEY="):
                    k = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    assert k, "no key"
    _KEY = k
    return k

STATS = {"calls": 0, "tokens": 0, "ms": []}

MOCK = bool(os.environ.get("JEV_MOCK"))  # JEV_MOCK=1: offline fake answers, no key, no network, no spend

def _mock(state, questions):
    import hashlib
    h = lambda q: int(hashlib.md5((state + json.dumps(q, sort_keys=True)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return {k: {"noul": h(q)} for k, q in questions.items()}

def _post(state, questions, tag, model="jev-1.13.0", retries=6):
    if MOCK: return _mock(state, questions)
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    for attempt in range(retries):
        req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=body,
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read())
            ms = (time.time() - t0) * 1000
            tok = out.get("usage", {}).get("input_tokens", 0)
            with _lock:
                STATS["calls"] += 1; STATS["tokens"] += tok; STATS["ms"].append(ms)
                with open(LEDGER, "a") as f:
                    f.write(json.dumps({"t": time.time(), "tag": tag, "tokens": tok, "ms": round(ms), "nq": len(questions), "model": out.get("model")}) + "\n")
            return out["answers"]
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            if e.code in (429, 500, 502, 503, 529) and attempt < retries - 1:
                time.sleep(1.0 * (attempt + 1)); continue
            raise RuntimeError(f"HTTP {e.code}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries - 1: time.sleep(1.0 * (attempt + 1)); continue
            raise

def ask_many(questions, state="", tag="", per_call=120, workers=16):
    """questions: dict id -> question. Splits into calls of `per_call` questions, runs concurrently."""
    items = list(questions.items())
    chunks = [dict(items[i:i + per_call]) for i in range(0, len(items), per_call)]
    out = {}
    with ThreadPoolExecutor(workers) as ex:
        for ans in ex.map(lambda c: _post(state, c, tag), chunks):
            out.update(ans)
    return out

def total_spend():
    if not os.path.exists(LEDGER): return 0.0
    return sum(json.loads(l)["tokens"] for l in open(LEDGER)) * PRICE

def spend_by_tag():
    d = {}
    if os.path.exists(LEDGER):
        for l in open(LEDGER):
            r = json.loads(l); d.setdefault(r["tag"], [0, 0]); d[r["tag"]][0] += 1; d[r["tag"]][1] += r["tokens"]
    return {k: {"calls": v[0], "tokens": v[1], "usd": round(v[1] * PRICE, 4)} for k, v in d.items()}
