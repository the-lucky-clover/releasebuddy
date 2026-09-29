"""Agent base: every agent has a name, a purpose, and a run(ctx) that returns a Result."""
from dataclasses import dataclass, field


@dataclass
class Result:
    agent: str
    ok: bool
    summary: str
    details: list = field(default_factory=list)

    def lines(self):
        icon = "✅" if self.ok else "❌"
        out = [f"{icon} [{self.agent}] {self.summary}"]
        out += [f"   - {d}" for d in self.details]
        return out


class Agent:
    name = "agent"
    purpose = "does a thing"

    def run(self, ctx):
        raise NotImplementedError
