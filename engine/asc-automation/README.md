# 1918: Ace of Aces — App Store Connect Autopilot

Tiny modular scripts that do the Apple Developer / App Store Connect busywork for you.
Each module does exactly ONE thing. `run-all.sh` runs them in order and stops if one fails.

## The deal

Some steps Apple forces you to do by hand (identity check, $99 payment).
Everything after that, the scripts handle.

### Manual steps (do these once, ~15 min total)

**Step 0 — Join the Apple Developer Program ($99/yr).** Can't be scripted (ID check + payment).
- iPhone: install the free **Apple Developer** app → Account → Enroll → **Individual**.
- Or: https://developer.apple.com/programs/enroll/
- Wait for the approval email (24–48 hrs). Nothing below works until it arrives.

**Step 1 — Create an App Store Connect API key.** Can't be scripted (it's the key TO the scripting).
1. Go to https://appstoreconnect.apple.com/access/integrations/api
   (or App Store Connect → Users and Access → Integrations → App Store Connect API)
2. Under **Team Keys**, click the **+** button.
3. Name: `asc-automation`. Access: **Admin**. Click **Generate**.
4. **Download the `.p8` file NOW — you only get one chance.** Save it somewhere safe, e.g. `engine/asc-automation (inside this repo)/AuthKey_XXXXXX.p8`.
5. Copy the **Key ID** (shown in the table) and the **Issuer ID** (shown at the top of the page).

**Step 2 — Fill in your config.**
```bash
cd engine/asc-automation (inside this repo)
cp config.env.example config.env
# open config.env and paste your 3 values + the path to your .p8 file
```

**Step 3 — Launch the autopilot.**
```bash
./run-all.sh
```

That's it. Go make coffee.

## What each module does

| Module | Does | Apple equivalent |
|---|---|---|
| `modules/01_register_bundle_id.py` | Registers `com.luckyclover.aceofaces` as an App ID | Developer portal → Identifiers → + → App IDs |
| `modules/02_enable_iap.py` | Turns on the In-App Purchase capability (needed for the $2.99 remove-ads) | App ID → Capabilities → In-App Purchase |
| `modules/03_create_app.py` | Creates the `1918: Ace of Aces` app record (SKU `ACEOFACES001`) | App Store Connect → My Apps → + → New App |

Every module is idempotent: run it twice and the second run just says "already done"
instead of exploding. Progress is saved in `.asc-state.json` (gitignored).

## Files

- `run-all.sh` — the orchestrator. Checks python3, installs deps, runs modules in order.
- `config.env` — YOUR secrets. Never commit this. Never share it.
- `lib/` — shared plumbing: config loading, JWT auth token minting, API helper.
- `requirements.txt` — `pyjwt`, `cryptography`, `requests`.

## Troubleshooting

- `config.env not found` → you skipped manual Step 2. `cp config.env.example config.env` and fill it in.
- `401 Unauthorized` → your Key ID / Issuer ID / .p8 path is wrong, or the key doesn't have Admin access.
- `409` on bundle ID → it already exists; the script will adopt it automatically.
- Apple approval email hasn't arrived → wait. The API rejects everything until enrollment is active.
