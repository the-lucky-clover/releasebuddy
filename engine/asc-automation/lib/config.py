"""Load config.env (simple KEY=VALUE parser, no dependencies)."""
import os

REQUIRED = ["ASC_KEY_ID", "ASC_ISSUER_ID", "ASC_P8_PATH"]


def load(repo_root):
    env_path = os.path.join(repo_root, "config.env")
    if not os.path.exists(env_path):
        raise SystemExit(
            "config.env not found.\n"
            "  cp config.env.example config.env\n"
            "then open config.env and paste your Key ID, Issuer ID, and .p8 path."
        )
    cfg = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    # Defaults for app values
    cfg.setdefault("BUNDLE_ID", "com.luckyclover.aceofaces")
    cfg.setdefault("APP_NAME", "1918: Ace of Aces")
    cfg.setdefault("APP_SKU", "ACEOFACES001")
    cfg.setdefault("APP_DESCRIPTION_NAME", "1918 Ace of Aces")

    missing = [k for k in REQUIRED if not cfg.get(k)]
    if missing:
        raise SystemExit(
            f"config.env is missing: {', '.join(missing)}\n"
            "Get them from App Store Connect → Users and Access → Integrations → "
            "App Store Connect API (https://appstoreconnect.apple.com/access/integrations/api)"
        )
    p8 = cfg["ASC_P8_PATH"]
    if not os.path.exists(os.path.expanduser(p8)):
        raise SystemExit(f".p8 key file not found at: {p8}\nCheck ASC_P8_PATH in config.env.")
    return cfg
