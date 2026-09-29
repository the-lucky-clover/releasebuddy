"""PREFLIGHT — the scout. Verifies credentials, config, and sanity.
Touches nothing. Finds the missing .p8 at step 0, not step 47."""
import os

from .base import Agent, Result


class PreflightAgent(Agent):
    name = "preflight"
    purpose = "verify credentials and config before anything touches a store"

    REQUIRED_BY_STORE = {
        "apple": ["ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_P8_PATH", "IOS_BUNDLE_ID"],
        "google": ["GOOGLE_SA_JSON", "ANDROID_PACKAGE"],
        "samsung": [],
        "amazon": [],
    }

    def run(self, ctx):
        cfg, store = ctx["cfg"], ctx["store"]
        problems, notes = [], []
        for key in self.REQUIRED_BY_STORE.get(store.id, []):
            val = cfg.get(key, "")
            if not val:
                problems.append(f"missing config: {key}")
            elif key.endswith(("_PATH", "_JSON")) and not os.path.exists(
                    os.path.expanduser(val)):
                problems.append(f"file not found: {key}={val}")
        for key in ["APP_NAME", "APP_FULL_DESC"]:
            if not cfg.get(key):
                problems.append(f"missing metadata: {key} (describe your app once!)")

        ok, msg = store.check_auth()
        notes.append(f"store auth: {msg}")
        if not ok:
            problems.append(f"store auth failed: {msg}")

        if problems:
            return Result(self.name, False, "preflight FAILED — fix these first",
                          problems + notes)
        return Result(self.name, True, "all clear — credentials and config check out",
                      notes)
