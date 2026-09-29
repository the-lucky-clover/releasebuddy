"""Apple App Store adapter (App Store Connect API).

Automates: bundle ID registration, IAP capability, app record creation.
Does NOT do: binary upload (Apple requires Xcode/Transporter — no API exists).
"""
import time

import jwt
import requests

from .base import StoreAdapter

API = "https://api.appstoreconnect.apple.com/v1"


class AppleAdapter(StoreAdapter):
    id = "apple"
    display = "Apple App Store"

    def _token(self):
        with open(self.cfg["ASC_P8_PATH"]) as f:
            key = f.read()
        now = int(time.time())
        return jwt.encode(
            {"iss": self.cfg["ASC_ISSUER_ID"], "iat": now,
             "exp": now + 15 * 60, "aud": "appstoreconnect-v1"},
            key, algorithm="ES256", headers={"kid": self.cfg["ASC_KEY_ID"]},
        )

    def _session(self):
        s = requests.Session()
        s.headers.update({"Authorization": f"Bearer {self._token()}",
                          "Content-Type": "application/json"})
        return s

    # --- interface ----------------------------------------------------
    def check_auth(self):
        try:
            r = self._session().get(API + "/apps", params={"limit": 1}, timeout=20)
            if r.status_code == 200:
                return True, "App Store Connect API reachable."
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as e:  # noqa: BLE001
            return False, f"Auth failed: {e}"

    def metadata_rules(self):
        return {"APP_NAME": 30, "APP_SUBTITLE": 30, "APP_KEYWORDS": 100,
                "APP_FULL_DESC": 4000, "APP_PROMO_TEXT": 170}

    def asset_rules(self):
        return {"icon_size": (1024, 1024), "min_screenshots": 2}

    def _ensure_bundle_id(self, s):
        bid = self.cfg["IOS_BUNDLE_ID"]
        found = s.get(API + "/bundleIds", params={"filter[identifier]": bid}).json()
        if found.get("data"):
            return found["data"][0]["id"], False
        r = s.post(API + "/bundleIds", json={"data": {
            "type": "bundleIds", "attributes": {
                "identifier": bid,
                "name": self.cfg.get("APP_NAME", bid),
                "platform": "IOS"}}})
        r.raise_for_status()
        return r.json()["data"]["id"], True

    def _ensure_iap(self, s, rid):
        caps = s.get(f"{API}/bundleIds/{rid}/bundleIdCapabilities").json()
        have = {c["attributes"]["capabilityType"] for c in caps.get("data", [])}
        if "IN_APP_PURCHASE" in have:
            return False
        r = s.post(f"{API}/bundleIds/{rid}/bundleIdCapabilities", json={"data": {
            "type": "bundleIdCapabilities",
            "attributes": {"capabilityType": "IN_APP_PURCHASE", "settings": []}}})
        r.raise_for_status()
        return True

    def _ensure_app(self, s, rid):
        bid = self.cfg["IOS_BUNDLE_ID"]
        apps = s.get(API + "/apps", params={"limit": 200}).json()
        match = next((a for a in apps.get("data", [])
                      if a["attributes"].get("bundleId") == bid), None)
        if match:
            return match["id"], False
        r = s.post(API + "/apps", json={"data": {
            "type": "apps",
            "attributes": {"name": self.cfg["APP_NAME"],
                           "primaryLocale": "en-US",
                           "sku": self.cfg.get("APP_SKU", bid)},
            "relationships": {"bundleId": {"data": {"type": "bundleIds", "id": rid}}}}})
        r.raise_for_status()
        return r.json()["data"]["id"], True

    def publish(self, ctx):
        s = self._session()
        steps = []
        rid, created = self._ensure_bundle_id(s)
        steps.append(f"bundle ID {'registered' if created else 'already registered'}: "
                     f"{self.cfg['IOS_BUNDLE_ID']}")
        iap = self._ensure_iap(s, rid)
        steps.append(f"In-App Purchase capability {'enabled' if iap else 'already enabled'}")
        app_id, created = self._ensure_app(s, rid)
        steps.append(f"app record {'created' if created else 'already exists'} "
                     f"(ASC id {app_id})")
        if ctx.get("dry_run"):
            steps.append("DRY RUN — no further changes made.")
        steps.append(
            "NEXT (manual, Apple gives no API): archive in Xcode → upload the .ipa "
            "with Transporter → then this tool can drive the submit-for-review flow.")
        return {"store": self.display, "dry_run": ctx.get("dry_run", True), "steps": steps}
