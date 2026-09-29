#!/usr/bin/env python3
"""Module 02: Enable the In-App Purchase capability on the App ID.
Needed later for the $2.99 remove-ads purchase.
Apple-portal equivalent: Identifiers → your App ID → Capabilities → In-App Purchase.
Idempotent: skips if already enabled.
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
    if not rid:
        raise SystemExit("No bundle ID in .asc-state.json — run module 01 first.")

    print("Checking capabilities on the App ID ...")
    caps = client.get(f"/bundleIds/{rid}/bundleIdCapabilities")
    have = {c["attributes"]["capabilityType"] for c in caps.get("data", [])}
    if "IN_APP_PURCHASE" in have:
        print("In-App Purchase already enabled. Nothing to do.")
    else:
        print("Enabling In-App Purchase ...")
        resp = client.post(
            f"/bundleIds/{rid}/bundleIdCapabilities",
            {
                "data": {
                    "type": "bundleIdCapabilities",
                    "attributes": {"capabilityType": "IN_APP_PURCHASE", "settings": []},
                }
            },
        )
        if resp.status_code == 409:
            print("Apple says it's already enabled. Moving on.")
        elif resp.status_code >= 400:
            client._boom(resp, "enable In-App Purchase capability")
        else:
            print("In-App Purchase enabled.")
    print("Module 02 DONE: IAP capability on.")


if __name__ == "__main__":
    main()
