"""Render the 40-second island video (docs/islands.mp4) and GIF (docs/islands.gif) frame by frame from Figure 1 of the study page
(web/index.html#islands), then encode with ffmpeg. Needs the static server at the repo root (python3 -m http.server 8765).
Usage: python darwin/render_video.py [--test]"""
import asyncio, glob, os, subprocess, sys
import imageio_ffmpeg
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "frames", "video"); os.makedirs(OUT, exist_ok=True)
CHROME = glob.glob(os.path.expanduser("~/Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell"))[0]
FPS, POLAR = 30, 93772
CAP = [
    (0, "Every island starts with the <em>same 300 random creatures</em>."),
    (4, "Jev, a judgment model, decides who finds food, who survives the winter, and who eats whom."),
    (13, "Nobody told it what a polar bear is."),
    (23, None),
    (26, "Tundra island, mean of 5 independent runs: insulating coats <em>21% → 90%</em>, white or pale <em>18% → 81%</em>."),
    (32, None),
]
def ease(x): return x * x * (3 - 2 * x)
def t_at(sec):
    if sec < 3: return 1.2 * ease(sec / 3) if sec > 0 else 0.0
    if sec < 26: return 1.2 + (80.65 - 1.2) * ease((sec - 3) / 23)
    return 80.65
def caption_at(sec):
    c = None
    for s, txt in CAP:
        if sec >= s: c = txt
    return c

async def main(test):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME)
        pg = await b.new_page(viewport={"width": 1280, "height": 1800})
        await pg.goto("http://localhost:8765/web/index.html?render=1&seed=1#islands")
        await pg.wait_for_function("window.__islandsReady === true", timeout=60000)
        box = "() => { const f = document.getElementById('fig-islands').getBoundingClientRect(), v = document.querySelector('#fig-islands .iview').getBoundingClientRect(); return [f.x, f.y, f.width, v.bottom - f.y]; }"
        dims = []
        for m in ("conv", "map"):
            await pg.evaluate("(m) => window.Islands.mode(m)", m); dims.append(await pg.evaluate(box))
        x, y, w, _ = dims[-1]
        clip = {"x": x - 24, "y": y - 12, "width": w + 48, "height": max(d[3] for d in dims) + 24}
        total = 40 * FPS
        frames = [int(x * FPS) for x in (2, 10, 20, 28, 34, 38.5)] if test else range(total)
        state = {"cap": "x", "pin": None, "ov": None}
        for f in frames:
            sec = f / FPS
            cap = caption_at(sec)
            if cap != state["cap"]:
                await pg.evaluate("(c) => window.Islands.caption(c)", cap); state["cap"] = cap
            pin = POLAR if 26 <= sec < 32 else -1
            ov = "conv" if 32 <= sec < 37 else ("web" if sec >= 37 else None)
            if ov != state["ov"]:
                await pg.evaluate("([m]) => window.Islands.mode(m, 0)", [ov]); state["ov"] = ov
            await pg.evaluate("([t, c]) => window.Islands.setT(t, c)", [t_at(sec), sec])
            if pin != state["pin"]:
                await pg.evaluate("(i) => window.Islands.pin(i)", pin); state["pin"] = pin
            await pg.screenshot(path=os.path.join(OUT, f"f{f:05d}.jpg"), type="jpeg", quality=93, clip=clip)
        await b.close()
    if not test:
        mp4 = os.path.join(ROOT, "docs", "islands.mp4")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(OUT, "f%05d.jpg"),
                        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:color=0xfaf9f5", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow", "-movflags", "+faststart", mp4], check=True)
        gif = os.path.join(ROOT, "docs", "islands.gif")
        vf = "fps=8,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(OUT, "f%05d.jpg"), "-vf", vf, "-loop", "0", gif], check=True)
        for f in (mp4, gif): print("wrote", f, round(os.path.getsize(f) / 1e6, 2), "MB")

asyncio.run(main("--test" in sys.argv))
