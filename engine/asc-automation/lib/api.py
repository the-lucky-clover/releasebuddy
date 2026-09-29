"""Thin wrapper around the App Store Connect API with human-readable errors."""
import json
import os
import sys

import requests

BASE = "https://api.appstoreconnect.apple.com/v1"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib import auth  # noqa: E402


class ASC:
    def __init__(self, cfg):
        self.cfg = cfg
        p8 = os.path.expanduser(cfg["ASC_P8_PATH"])
        self.token = auth.mint_token(p8, cfg["ASC_KEY_ID"], cfg["ASC_ISSUER_ID"])
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )

    def _boom(self, resp, what):
        try:
            detail = json.dumps(resp.json(), indent=2)[:800]
        except Exception:
            detail = resp.text[:800]
        raise SystemExit(f"\nFAILED: {what}\nHTTP {resp.status_code}\n{detail}")

    def get(self, path, params=None):
        r = self.session.get(BASE + path, params=params or {})
        if r.status_code >= 400:
            self._boom(r, f"GET {path}")
        return r.json()

    def post(self, path, body):
        r = self.session.post(BASE + path, json=body)
        return r


def load_state(repo_root):
    p = os.path.join(repo_root, ".asc-state.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return {}


def save_state(repo_root, state):
    p = os.path.join(repo_root, ".asc-state.json")
    with open(p, "w") as f:
        json.dump(state, f, indent=2)
