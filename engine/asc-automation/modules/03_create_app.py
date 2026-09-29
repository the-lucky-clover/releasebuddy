#!/usr/bin/env python3
"""Module 03: Create the '1918: Ace of Aces' app record in App Store Connect.
Portal equivalent: My Apps → + → New App (platform iOS, name, English (U.S.), bundle ID, SKU).
Idempotent: if an app with this bundle ID already exists, it adopts it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from lib import config, api  # noqa: E402

REPO = os.path.join(os.path.dirname(__file__), "..")


def main():
    cfg = config.load(REPO)
    client = api.ASC(cfg)
    state = api.load_state(REPO)
    rid = state.get("bundle_id_resource_id")
    bundle_id = state.get("bundle_id", cfg["BUNDLE_ID"])
    if not rid:
        raise SystemExit("No bundle ID in .asc-state.json — run modules 01 and 02 first.")

    print(f"Looking for an existing app with bundle ID '{bundle_id}' ...")
    apps = client.get("/apps", params={"limit": 200})
    match = next(
        (a for a in apps.get("data", []) if a["attributes"].get("bundleId") == bundle_id),
        None,
    )
    if match:
        app_id = match["id"]
        print(f"App already exists: '{match['attributes']['name']}' (id {app_id}). Adopting it.")
    else:
        print(f"Creating app '{cfg['APP_NAME']}' ...")
        resp = client.post(
            "/apps",
            {
                "data": {
                    "type": "apps",
                    "attributes": {
                        "name": cfg["APP_NAME"],        # max 30 chars
                        "primaryLocale": "en-US",       # English (U.S.)
                        "sku": cfg["APP_SKU"],
                    },
                    "relationships": {
                        "bundleId": {"data": {"type": "bundleIds", "id": rid}}
                    },
                }
            },
        )
        if resp.status_code >= 400:
            client._boom(resp, "create app")
        app = resp.json()["data"]
        app_id = app["id"]
        print(f"Created! App Store Connect ID: {app_id}")

    state["app_resource_id"] = app_id
    api.save_state(REPO, state)
    print("Module 03 DONE: app record exists in App Store Connect.")


if __name__ == "__main__":
    main()
