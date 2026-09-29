"""Mint a short-lived JWT for the App Store Connect API (ES256, 20 min max)."""
import time
import jwt


def mint_token(p8_path, key_id, issuer_id):
    with open(p8_path) as f:
        private_key = f.read()
    now = int(time.time())
    payload = {
        "iss": issuer_id,
        "iat": now,
        "exp": now + 15 * 60,  # 15 min, safely under Apple's 20-min cap
        "aud": "appstoreconnect-v1",
    }
    return jwt.encode(payload, private_key, algorithm="ES256", headers={"kid": key_id})
