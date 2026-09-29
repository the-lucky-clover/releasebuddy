#!/usr/bin/env python3
"""ring — one command to rule every app store.

Usage:
  python3 ring.py --store apple preflight
  python3 ring.py --store apple lint
  python3 ring.py --store apple assets
  python3 ring.py --store google release --dry-run
  python3 ring.py --store google release --track internal --aab app-release.aab
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)

from agents.base import Result  # noqa: E402
from agents.preflight import PreflightAgent  # noqa: E402
from agents.metadata_lint import LintAgent  # noqa: E402
from agents.asset_check import AssetAgent  # noqa: E402
from agents.docs_gen import DocsAgent  # noqa: E402
from agents.shots import ShotsAgent  # noqa: E402
from agents.github_publish import GithubAgent  # noqa: E402
from agents.publish import PublishAgent  # noqa: E402
from agents.reporter import ReporterAgent  # noqa: E402
from stores.apple import AppleAdapter  # noqa: E402
from stores.google import GoogleAdapter  # noqa: E402
from stores.samsung import SamsungAdapter  # noqa: E402
from stores.amazon import AmazonAdapter  # noqa: E402

STORES = {s.id: s for s in (AppleAdapter, GoogleAdapter, SamsungAdapter, AmazonAdapter)}

AGENTS = {
    "preflight": PreflightAgent(),
    "lint": LintAgent(),
    "assets": AssetAgent(),
    "docs": DocsAgent(),
    "shots": ShotsAgent(),
    "github": GithubAgent(),
    "release": None,  # runbook, not a single agent
}

RELEASE_RUNBOOK = [PreflightAgent(), LintAgent(), AssetAgent(), DocsAgent(),
                   ShotsAgent(), GithubAgent(), PublishAgent()]


def load_config():
    path = os.path.join(REPO, "config.env")
    if not os.path.exists(path):
        sys.exit("config.env not found.\n"
                 "  cp config/config.env.example config.env\n"
                 "then fill in your store credentials + app metadata.")
    cfg = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    return cfg


def main():
    ap = argparse.ArgumentParser(prog="ring",
                                 description="One command to rule every app store.")
    ap.add_argument("--store", required=True, choices=sorted(STORES),
                    help="which store to target")
    ap.add_argument("command", choices=["preflight", "lint", "assets", "docs",
                                                     "shots", "github", "release"],
                    help="which agent (or full release runbook) to run")
    ap.add_argument("--dry-run", action="store_true", default=False,
                    help="rehearse only; publish nothing (strongly recommended first)")
    ap.add_argument("--track", default="internal",
                    help="Play track for release (internal/alpha/beta/production)")
    ap.add_argument("--aab", default=None, help="path to signed .aab (Google)")
    ap.add_argument("--staged-fraction", type=float, default=None,
                    help="e.g. 0.1 = staged rollout to 10%% (Google)")
    args = ap.parse_args()

    cfg = load_config()
    store = STORES[args.store](cfg)
    ctx = {"cfg": cfg, "store": store, "repo": REPO,
           "dry_run": args.dry_run, "track": args.track,
           "aab_path": args.aab, "staged_fraction": args.staged_fraction,
           "command": args.command, "results": []}

    if args.command == "release" and not args.dry_run:
        print("⚠️  LIVE release requested. The publisher will make real changes.")
        print("   Run with --dry-run first if you haven't. Continuing in 3s... (Ctrl-C to stop)")
        import time
        time.sleep(3)

    plan = RELEASE_RUNBOOK if args.command == "release" else [AGENTS[args.command]]
    failed = False
    for agent in plan:
        print(f"\n—— {agent.name}: {agent.purpose} ——")
        result = agent.run(ctx)
        ctx["results"].append(result)
        for line in result.lines():
            print(line)
        if not result.ok and args.command == "release":
            print("\nRunbook halted: fix the failure above, then re-run.")
            failed = True
            break

    if args.command == "release" or True:
        rep = ReporterAgent().run(ctx)
        for line in rep.lines():
            print(line)

    sys.exit(1 if failed or any(not r.ok for r in ctx["results"]) else 0)


if __name__ == "__main__":
    main()
