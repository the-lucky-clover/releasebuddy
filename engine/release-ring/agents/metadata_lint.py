"""LINT — the scholar. Checks your copy against each store's real character limits.
No more 'rejected: metadata' emails."""
from .base import Agent, Result


class LintAgent(Agent):
    name = "lint"
    purpose = "validate listing copy against store character limits"

    def run(self, ctx):
        cfg, store = ctx["cfg"], ctx["store"]
        rules = store.metadata_rules()
        violations, notes = [], []
        if not rules:
            return Result(self.name, True, "no lint rules for this store (stub?)", notes)
        for field_name, max_chars in rules.items():
            value = cfg.get(field_name, "")
            n = len(value)
            if not value:
                violations.append(f"{field_name}: empty (limit {max_chars})")
            elif n > max_chars:
                violations.append(
                    f"{field_name}: {n} chars, limit {max_chars} — trim {n - max_chars}")
            else:
                notes.append(f"{field_name}: {n}/{max_chars} chars ✓")
        if violations:
            return Result(self.name, False,
                          f"{len(violations)} metadata violation(s) for {store.display}",
                          violations + notes)
        return Result(self.name, True,
                      f"copy fits {store.display} limits", notes)
