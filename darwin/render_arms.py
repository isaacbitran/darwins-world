"""Drive the arms-race figure of the study page (web/index.html#arms) in headless Chromium to make docs/hero.gif and docs/darwins-world.mp4.

Needs a static server at the repo root:  python3 -m http.server 8765
  python darwin/render_arms.py --shot out.png [--q "world=locked&rules=po&seed=1"] [--t 300]   # one screenshot, prints console errors
  python darwin/render_arms.py                                                                  # frames -> GIF + MP4
"""
import argparse, asyncio, glob, os, shutil, subprocess
import imageio_ffmpeg
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = os.path.join(ROOT, "frames", "arms")
URL = "http://localhost:8765/web/index.html?render=1"
VIEW = (1280, 1800)
FPS = 30

# The script: (world, rules, seed, start gen, end gen, seconds, caption). Generations are eased within each scene.
SCENES = [
    ("locked", "po", "1", 0, 0, 3.0, "64 prey and 64 predator designs. Jev answered <em>4,096</em> questions: does this predator catch this prey?"),
    ("locked", "po", "1", 0, 600, 13.0, "No fitness function. Each side's best design depends on what the other side is right now."),
    ("locked", "po", "1", 600, 600, 4.0, "The most common prey design changed <em>7 to 12 times</em> per run. With no pairwise interactions: <em>0</em>."),
    ("savanna", "po", "4", 0, 600, 9.0, "Earth river valley, run 4: <em>13</em> changes. With fixed predators: 0 to 5."),
    ("savanna", "default", "1", 0, 600, 6.0, "When Jev's habitat-fit score also selects: <em>0</em> changes in 13 of 15 runs, a hill-climb."),
]

def ease(x): return x * x * (3 - 2 * x)

async def page(p, w=VIEW[0], h=VIEW[1]):
    chrome = glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell"))
    b = await p.chromium.launch(executable_path=chrome[0]) if chrome else await p.chromium.launch()
    pg = await b.new_page(viewport={"width": w, "height": h})
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    return b, pg, errs

async def open_fig(pg, q=""):
    await pg.goto(f"{URL}{'&' + q if q else ''}#arms")
    await pg.wait_for_function("window.__armsReady === true", timeout=60000)
    # the clip: figure header through the two strategy streams
    return await pg.evaluate("""() => { const f = document.getElementById('fig-arms').getBoundingClientRect(),
        s = document.querySelector('#fig-arms .streams').getBoundingClientRect();
        return {x: f.x - 24, y: f.y + window.scrollY - 12, width: f.width + 48, height: s.bottom - f.y + 30}; }""")

async def shot(out, q, t, w=VIEW[0], h=VIEW[1]):
    async with async_playwright() as p:
        b, pg, errs = await page(p, w, h)
        clip = await open_fig(pg, q)
        await pg.evaluate(f"window.Arms.setT({t})")
        await pg.wait_for_timeout(300)
        await pg.screenshot(path=out, clip=clip)
        print("console errors:", errs)
        await b.close()

async def render():
    shutil.rmtree(FRAMES, ignore_errors=True); os.makedirs(FRAMES)
    async with async_playwright() as p:
        b, pg, errs = await page(p)
        clip = await open_fig(pg)
        n = 0
        for world, rules, seed, g0, g1, secs, cap in SCENES:
            await pg.evaluate("([w, r, s]) => window.Arms.set(w, r, s)", [world, rules, seed])
            await pg.evaluate("(c) => window.Arms.caption(c)", cap)
            k = int(secs * FPS)
            for f in range(k):
                g = g0 + (g1 - g0) * ease(f / max(k - 1, 1))
                await pg.evaluate("(t) => window.Arms.setT(t)", g)
                await pg.screenshot(path=os.path.join(FRAMES, f"f{n:05d}.png"), clip=clip)
                n += 1
        print("frames:", n, "console errors:", errs)
        await b.close()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    src = ["-framerate", str(FPS), "-i", os.path.join(FRAMES, "f%05d.png")]
    even = ["-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=0xfaf9f5"]
    mp4 = os.path.join(ROOT, "docs", "darwins-world.mp4")
    subprocess.run([ff, "-y", "-loglevel", "error", *src, *even, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "24",
                    "-preset", "slow", "-movflags", "+faststart", mp4], check=True)
    gif = os.path.join(ROOT, "docs", "hero.gif")
    vf = "fps=10,scale=880:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
    subprocess.run([ff, "-y", "-loglevel", "error", *src, "-vf", vf, "-loop", "0", gif], check=True)
    for f in (mp4, gif): print("wrote", f, round(os.path.getsize(f) / 1e6, 2), "MB")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot"); ap.add_argument("--q", default="world=locked&rules=po&seed=1"); ap.add_argument("--t", type=float, default=300)
    ap.add_argument("--size", default=f"{VIEW[0]}x{VIEW[1]}")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    asyncio.run(shot(a.shot, a.q, a.t, W, H) if a.shot else render())
