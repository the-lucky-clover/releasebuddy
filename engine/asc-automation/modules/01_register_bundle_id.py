#!/usr/bin/env python3
"""Module 01: Register the bundle ID (App ID) for 1918: Ace of Aces.
Apple-portal equivalent: Certificates, Identifiers & Profiles → Identifiers → + → App IDs.
Idempotent: if the bundle ID already exists, it adopts it and moves on.
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
    bundle_id = cfg["BUNDLE_ID"]

    print(f"Looking for existing App ID '{bundle_id}' ...")
    existing = client.get("/bundleIds", params={"filter[identifier]": bundle_id})
    if existing.get("data"):
        rid = existing["data"][0]["id"]
        print(f"Already registered. Adopting existing App ID (resource id {rid}).")
    else:
        print(f"Registering new App ID '{bundle_id}' ...")
        resp = client.post(
            "/bundleIds",
            {
                "data": {
                    "type": "bundleIds",
                    "attributes": {
                        "identifier": bundle_id,
                        "name": cfg["APP_DESCRIPTION_NAME"],
                        "platform": "IOS",
                    },
                }
            },
        )
        if resp.status_code == 409:
            # Race / already there — fetch it instead of dying.
            print("Apple says it already exists; fetching it ...")
            existing = client.get("/bundleIds", params={"filter[identifier]": bundle_id})
            rid = existing["data"][0]["id"]
        elif resp.status_code >= 400:
            client._boom(resp, "register bundle ID")
        else:
            rid = resp.json()["data"]["id"]
            print(f"Registered. Resource id: {rid}")

    state["bundle_id"] = bundle_id
    state["bundle_id_resource_id"] = rid
    api.save_state(REPO, state)
    print("Module 01 DONE: bundle ID registered.")


if __name__ == "__main__":
    main()
