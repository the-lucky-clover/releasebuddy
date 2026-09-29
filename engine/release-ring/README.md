# One Ring — multi-store release agents

`ring` carries your app to every major commercial app store with one command.
See [TREATMENT.md](TREATMENT.md) for the vision; this file is the operator's manual.

## Stores

| ID | Store | Status |
|---|---|---|
| `apple` | Apple App Store | ✅ Working (App Store Connect API) |
| `google` | Google Play | ✅ Working (Play Developer API, service account) |
| `samsung` | Samsung Galaxy Store | 🧱 Stub — adapter interface documented, needs Seller Portal API creds |
| `amazon` | Amazon Appstore | 🧱 Stub — adapter interface documented, needs developer creds |

## Setup (once per store)

**Apple** (also see `../asc-automation/` for the standalone Apple autopilot):
1. Enroll in the Apple Developer Program — https://developer.apple.com/programs/enroll/
2. Create an Admin API key: https://appstoreconnect.apple.com/access/integrations/api
   (download the `.p8` once; copy Key ID + Issuer ID)
3. Fill in `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_P8_PATH` in `config.env`.

**Google**:
1. In Google Play Console, create a service account with release permissions
   (Setup → API access). Download the JSON key.
2. Fill in `GOOGLE_SA_JSON` (path) and `ANDROID_PACKAGE` in `config.env`.
3. API docs: https://developers.google.com/android-publisher

Then describe your app once:
```bash
cp config/config.env.example config.env   # then fill it in
```

## Usage

```bash
python3 ring.py --store apple preflight     # check credentials + config, touch nothing
python3 ring.py --store apple lint          # metadata character-limit check
python3 ring.py --store apple assets        # icon/screenshot sanity check
python3 ring.py --store apple docs          # generate privacy policy + support page
python3 ring.py --store apple shots         # capture screenshots at store sizes
python3 ring.py --store apple github        # push docs to GitHub Pages → live URLs
python3 ring.py --store google release --dry-run     # full rehearsal, publishes nothing
python3 ring.py --store google release --track internal --aab app-release.aab
```

`release` runs the whole fellowship in order: preflight → lint → assets → docs →
shots → github → publisher → reporter. Omit `--dry-run` only when you mean it.

## The full fellowship

| Agent | Role |
|---|---|
| `preflight` | the scout — creds + config check, touches nothing |
| `lint` | the scholar — copy vs. each store's character limits |
| `assets` | the quartermaster — icon + screenshot sanity |
| `docs` | the scribe — privacy policy + support page (md + html), AdMob disclosed honestly |
| `shots` | the photographer — captures screenshots at exact store resolutions via headless Chromium |
| `github` | the herald — pushes docs to GitHub, enables Pages → live privacy/support URLs |
| `publisher` | the envoy — the store's native API, dry-run first always |
| `reporter` | the bard — markdown tale of every run in `reports/` |

## Project layout

- `ring.py` — the one CLI to rule them all
- `agents/` — the fellowship (preflight, lint, assets, publisher, reporter)
- `stores/` — one adapter per store (apple, google, + stubs)
- `config/` — your one description of the app
- `reports/` — the bard's tales of each run

## Honest limits

- Apple binary upload still goes through Xcode/Transporter (Apple allows no other
  road); the Apple publisher automates everything around it and tells you the exact
  Transporter step.
- Nothing here has been run against a live store — no credentials exist yet.
  Every adapter was written against the public API docs; first live run should be
  `--dry-run`.
