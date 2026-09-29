"""PUBLISHER — the envoy. Speaks the store's native API. Dry-run first, always."""
from .base import Agent, Result


class PublishAgent(Agent):
    name = "publisher"
    purpose = "drive the store's publish flow (or rehearse it)"

    def run(self, ctx):
        store = ctx["store"]
        try:
            summary = store.publish(ctx)
        except SystemExit as e:
            return Result(self.name, False, f"publisher stopped: {e}", [])
        except Exception as e:  # noqa: BLE001
            return Result(self.name, False, f"publish failed: {e}", [])
        tag = "DRY RUN" if summary.get("dry_run") else "LIVE"
        return Result(self.name, True,
                      f"publisher finished [{tag}] on {summary.get('store')}",
                      summary.get("steps", []))
