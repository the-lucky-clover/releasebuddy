"""Store adapter interface. A new store = one new module implementing this."""
import os


class StoreAdapter:
    id = "base"
    display = "Base Store"

    def __init__(self, cfg):
        self.cfg = cfg

    # --- capabilities -------------------------------------------------
    def check_auth(self):
        """Verify credentials work. Returns (ok: bool, message: str). Touches nothing."""
        raise NotImplementedError

    def metadata_rules(self):
        """Returns {field_name: max_chars} for the lint agent."""
        return {}

    def asset_rules(self):
        """Returns dict like {'icon_size': (1024,1024), 'min_screenshots': 2}."""
        return {}

    def publish(self, ctx):
        """Run the store's publish flow. ctx has dry_run, track, aab_path, etc.
        Returns a dict summary for the reporter."""
        raise NotImplementedError


def repo_root():
    return os.path.join(os.path.dirname(__file__), "..")
