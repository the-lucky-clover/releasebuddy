"""ASSETS — the quartermaster. Confirms icon + screenshots exist and are shaped right.
Dimension checks run only if Pillow is installed; otherwise it checks presence."""
import os

from .base import Agent, Result


class AssetAgent(Agent):
    name = "assets"
    purpose = "verify icon and screenshots before a store complains"

    def run(self, ctx):
        store = ctx["store"]
        rules = store.asset_rules()
        assets_dir = os.path.join(ctx["repo"], "assets")
        problems, notes = [], []

        icon = os.path.join(assets_dir, "icon.png")
        if not os.path.exists(icon):
            problems.append("assets/icon.png missing — every store needs an icon")
        else:
            notes.append("icon.png present")
            want = rules.get("icon_size")
            if want:
                try:
                    from PIL import Image
                    w, h = Image.open(icon).size
                    if (w, h) == want:
                        notes.append(f"icon is {w}x{h} ✓")
                    else:
                        problems.append(f"icon is {w}x{h}, {store.display} wants "
                                        f"{want[0]}x{want[1]}")
                except ImportError:
                    notes.append("Pillow not installed — skipping dimension check "
                                 "(pip install pillow for pixel-level verification)")

        shots_dir = os.path.join(assets_dir, "screenshots")
        shots = []
        if os.path.isdir(shots_dir):
            shots = [f for f in os.listdir(shots_dir)
                     if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        want_n = rules.get("min_screenshots", 0)
        if len(shots) < want_n:
            problems.append(f"only {len(shots)} screenshot(s) in assets/screenshots/, "
                            f"{store.display} wants at least {want_n}")
        else:
            notes.append(f"{len(shots)} screenshot(s) present ✓")

        if problems:
            return Result(self.name, False, "asset problems found", problems + notes)
        return Result(self.name, True, "assets look shippable", notes)
