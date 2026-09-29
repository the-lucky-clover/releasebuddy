"""HERALD — pushes docs/ to GitHub and enables GitHub Pages, producing the live
privacy/support URLs your store listings require.

Needs GITHUB_TOKEN in config.env (token with `repo` scope; classic PAT is fine).
If the token is missing, fails with exact baby steps instead of a traceback.
"""
import os
import subprocess

import requests

from .base import Agent, Result

GH = "https://api.github.com"


class GithubAgent(Agent):
    name = "github"
    purpose = "publish docs to GitHub Pages → live privacy/support URLs"

    def _git(self, cwd, *args):
        r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()[:300]}")
        return r.stdout.strip()

    def run(self, ctx):
        cfg = ctx["cfg"]
        token = cfg.get("GITHUB_TOKEN", "").strip()
        repo_name = cfg.get("GITHUB_REPO", "1918-ace-of-aces-docs").strip()
        if not token:
            return Result(
                self.name, False, "no GITHUB_TOKEN — the herald has no voice",
                ["1. Go to https://github.com/settings/tokens/new",
                 "2. Note: 'ring-docs', expiration 90 days, check the `repo` scope",
                 "3. Generate token → copy it (you only see it once)",
                 "4. Paste it into config.env as GITHUB_TOKEN=...",
                 "5. Re-run. (Your UrgentSee-beta push is waiting on this same step, "
                 "by the way — one token unblocks both.)"])
        docs = os.path.join(ctx["repo"], "docs")
        if not os.path.exists(os.path.join(docs, "privacy.html")):
            return Result(self.name, False, "docs/privacy.html missing",
                          ["Run the docs agent first: ring --store <id> docs"])

        H = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
        me = requests.get(f"{GH}/user", headers=H, timeout=20).json()
        owner = me.get("login")
        if not owner:
            return Result(self.name, False, "GitHub token rejected",
                          [f"GitHub said: {str(me)[:200]}",
                           "Check the token is copied fully and has the `repo` scope."])

        r = requests.get(f"{GH}/repos/{owner}/{repo_name}", headers=H, timeout=20)
        if r.status_code == 404:
            c = requests.post(f"{GH}/user/repos", headers=H, timeout=20, json={
                "name": repo_name,
                "description": f"Privacy policy + support docs for {cfg.get('APP_NAME', 'app')}",
                "private": False, "auto_init": False})
            if c.status_code >= 400:
                return Result(self.name, False, "couldn't create repo",
                              [f"GitHub said: {c.text[:200]}"])
            details = [f"created public repo {owner}/{repo_name}"]
        elif r.status_code >= 400:
            return Result(self.name, False, "GitHub API error", [r.text[:200]])
        else:
            details = [f"using existing repo {owner}/{repo_name}"]

        remote = f"https://{token}@github.com/{owner}/{repo_name}.git"
        try:
            if not os.path.exists(os.path.join(docs, ".git")):
                self._git(docs, "init", "-b", "main")
            self._git(docs, "add", "-A")
            self._git(docs, "-c", "user.name=ring-herald", "-c",
                      "user.email=herald@localhost", "commit", "-m",
                      "docs: publish privacy + support", "--allow-empty")
            try:
                self._git(docs, "remote", "add", "origin", remote)
            except RuntimeError:
                self._git(docs, "remote", "set-url", "origin", remote)
            self._git(docs, "push", "-u", "origin", "main")
            details.append("docs pushed to main")
        except RuntimeError as e:
            return Result(self.name, False, "git push failed", [str(e)])

        p = requests.post(f"{GH}/repos/{owner}/{repo_name}/pages", headers=H,
                          timeout=20,
                          json={"source": {"branch": "main", "path": "/"}})
        if p.status_code not in (201, 409):
            details.append(f"Pages enable needs a click: {p.text[:150]} "
                           f"(or enable at github.com/{owner}/{repo_name}/settings/pages)")
        pages = requests.get(f"{GH}/repos/{owner}/{repo_name}/pages",
                             headers=H, timeout=20).json()
        base = pages.get("html_url") or f"https://{owner}.github.io/{repo_name}/"
        privacy_url = base + "privacy.html"
        support_url = base + "support.html"
        details += [f"PRIVACY_URL → {privacy_url}", f"SUPPORT_URL → {support_url}",
                    "paste these into your App Store Connect / Play Console listings"]
        return Result(self.name, True, "docs are live on GitHub Pages", details)
