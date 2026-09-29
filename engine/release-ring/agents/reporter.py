"""REPORTER — the bard. Writes the tale of the run so future-you knows
exactly what past-you shipped."""
import datetime
import os

from .base import Agent, Result


class ReporterAgent(Agent):
    name = "reporter"
    purpose = "write a run report to reports/"

    def run(self, ctx):
        results = ctx["results"]
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        store_id = ctx["store"].id
        cmd = ctx.get("command", "run")
        fname = f"{stamp}-{store_id}-{cmd}.md"
        reports_dir = os.path.join(ctx["repo"], "reports")
        os.makedirs(reports_dir, exist_ok=True)

        all_ok = all(r.ok for r in results)
        lines = [f"# Ring run — {store_id} / {cmd}",
                 f"_When: {stamp}_",
                 f"_Dry run: {ctx.get('dry_run', True)}_",
                 "",
                 f"**Verdict: {'ALL CLEAR' if all_ok else 'FAILURES — see below'}**",
                 ""]
        for r in results:
            lines += [f"## {r.agent} — {'pass' if r.ok else 'FAIL'}",
                      r.summary, ""]
            lines += [f"- {d}" for d in r.details] + [""]

        path = os.path.join(reports_dir, fname)
        with open(path, "w") as f:
            f.write("\n".join(lines))
        return Result(self.name, True, f"report written: reports/{fname}", [])
