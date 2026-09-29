"""Google Play adapter (Android Publisher API v3, service-account auth).

Full flow: insert edit → upload .aab → update listing → set track release →
validate → commit (or discard on dry-run).
Docs: https://developers.google.com/android-publisher
"""
import json
import os
import time

import jwt
import requests

from .base import StoreAdapter

API = "https://androidpublisher.googleapis.com/androidpublisher/v3/applications"


class GoogleAdapter(StoreAdapter):
    id = "google"
    display = "Google Play"

    def _access_token(self):
        with open(os.path.expanduser(self.cfg["GOOGLE_SA_JSON"])) as f:
            sa = json.load(f)
        now = int(time.time())
        assertion = jwt.encode(
            {"iss": sa["client_email"],
             "scope": "https://www.googleapis.com/auth/androidpublisher",
             "aud": "https://oauth2.googleapis.com/token",
             "iat": now, "exp": now + 3600},
            sa["private_key"], algorithm="RS256")
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion}, timeout=20)
        r.raise_for_status()
        return r.json()["access_token"]

    def _session(self):
        s = requests.Session()
        s.headers.update({"Authorization": f"Bearer {self._access_token()}"})
        return s

    # --- interface ----------------------------------------------------
    def check_auth(self):
        try:
            s = self._session()
            pkg = self.cfg["ANDROID_PACKAGE"]
            # Insert + immediately delete an edit: proves auth without changing anything.
            edit = s.post(f"{API}/{pkg}/edits", json={}).json()
            s.delete(f"{API}/{pkg}/edits/{edit['id']}")
            return True, f"Play API reachable for package {pkg}."
        except Exception as e:  # noqa: BLE001
            return False, f"Auth failed: {e}"

    def metadata_rules(self):
        return {"APP_NAME": 30, "APP_SHORT_DESC": 80, "APP_FULL_DESC": 4000}

    def asset_rules(self):
        return {"icon_size": (512, 512), "min_screenshots": 2}

    def publish(self, ctx):
        s = self._session()
        pkg = self.cfg["ANDROID_PACKAGE"]
        steps = []
        edit = s.post(f"{API}/{pkg}/edits", json={}).json()
        eid = edit["id"]
        steps.append(f"edit opened: {eid}")
        try:
            aab = ctx.get("aab_path") or self.cfg.get("AAB_PATH")
            version_codes = []
            if aab and os.path.exists(os.path.expanduser(aab)):
                with open(os.path.expanduser(aab), "rb") as f:
                    up = s.post(f"{API}/{pkg}/edits/{eid}/bundles",
                                files={"file": f}).json()
                version_codes = [up["versionCode"]]
                steps.append(f"uploaded bundle → versionCode {up['versionCode']}")
            else:
                steps.append("no .aab provided — metadata/track update only")

            lang = "en-US"
            s.put(f"{API}/{pkg}/edits/{eid}/listings/{lang}", json={
                "language": lang,
                "title": self.cfg["APP_NAME"][:30],
                "shortDescription": self.cfg.get("APP_SHORT_DESC", "")[:80],
                "fullDescription": self.cfg.get("APP_FULL_DESC", "")[:4000],
            }).raise_for_status()
            steps.append("store listing updated (en-US)")

            track = ctx.get("track", "internal")
            release = {"status": "completed"}
            if version_codes:
                release["versionCodes"] = version_codes
            if ctx.get("staged_fraction"):
                release["status"] = "inProgress"
                release["userFraction"] = ctx["staged_fraction"]
            s.post(f"{API}/{pkg}/edits/{eid}/tracks/{track}",
                   json={"track": track, "releases": [release]}).raise_for_status()
            steps.append(f"track '{track}' release staged ({release['status']})")

            s.post(f"{API}/{pkg}/edits/{eid}:validate").raise_for_status()
            steps.append("edit validated")

            if ctx.get("dry_run"):
                s.delete(f"{API}/{pkg}/edits/{eid}")
                steps.append("DRY RUN — edit discarded, nothing published.")
            else:
                s.post(f"{API}/{pkg}/edits/{eid}:commit").raise_for_status()
                steps.append("edit COMMITTED — release is live in Play Console.")
        except Exception:
            try:
                s.delete(f"{API}/{pkg}/edits/{eid}")
            except Exception:  # noqa: BLE001
                pass
            raise
        return {"store": self.display, "dry_run": ctx.get("dry_run", True),
                "track": ctx.get("track", "internal"), "steps": steps}
