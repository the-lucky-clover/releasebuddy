"""PHOTOGRAPHER — captures store screenshots at exact required resolutions.

Two modes:
1. CAPTURE: if SHOT_URL is set (a playable URL of your game), headless
   Chromium (playwright) screenshots it at each required size.
2. ADOPT: if assets/screenshots/<store>/ already holds enough shots, they're
   adopted as-is (idempotent — never re-captures over your work).

Sizes (portrait):
  Apple:  1290x2796 (6.7"), 1242x2688 (6.5"), 1242x2208 (5.5"), 2048x2732 (iPad)
  Google: 1080x1920 (9:16 — inside Play's 320px..3840px limits)
"""
import os

from .base import Agent, Result

APPLE_SIZES = [(1290, 2796), (1242, 2688), (1242, 2208), (2048, 2732)]
GOOGLE_SIZES = [(1080, 1920)]
IMG_EXTS = (".png", ".jpg", ".jpeg")


class ShotsAgent(Agent):
    name = "shots"
    purpose = "capture store screenshots at exact required resolutions"

    def run(self, ctx):
        store, cfg = ctx["store"], ctx["cfg"]
        sizes = {"apple": APPLE_SIZES, "google": GOOGLE_SIZES}.get(store.id)
        if not sizes:
            return Result(self.name, True,
                          f"no screenshot rules for {store.display} (stub) — skipping",
                          [])
        outdir = os.path.join(ctx["repo"], "assets", "screenshots", store.id)
        os.makedirs(outdir, exist_ok=True)
        have = [f for f in os.listdir(outdir)
                if f.lower().endswith(IMG_EXTS)] if os.path.isdir(outdir) else []
        if len(have) >= len(sizes):
            return Result(self.name, True,
                          f"{len(have)} screenshot(s) already in "
                          f"assets/screenshots/{store.id}/ — adopting them", have)

        url = cfg.get("SHOT_URL", "").strip()
        if not url:
            return Result(
                self.name, False, "no screenshots yet and no SHOT_URL to capture from",
                ["Option A: set SHOT_URL in config.env to a playable URL of your game "
                 "(e.g. your published web build) and re-run — I'll capture every "
                 "required size automatically.",
                 "Option B: drop screenshot files manually into "
                 f"assets/screenshots/{store.id}/ and re-run — I'll adopt them."])
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return Result(
                self.name, False, "playwright not installed",
                ["Install it once: .venv/bin/pip install -r requirements-shots.txt",
                 "then: .venv/bin/playwright install chromium",
                 "and re-run. (Kept out of base requirements — it's a ~150MB browser.)"])

        made = []
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for w, h in sizes:
                page = browser.new_page(viewport={"width": w, "height": h})
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(3000)  # let the game boot/animate in
                fname = f"shot-{w}x{h}.png"
                page.screenshot(path=os.path.join(outdir, fname))
                made.append(f"{fname} ({w}x{h})")
                page.close()
            browser.close()
        return Result(self.name, True,
                      f"captured {len(made)} screenshot(s) from {url}", made)
