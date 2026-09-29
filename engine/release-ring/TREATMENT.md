# TREATMENT: "ONE RING"

*A film-treatment-style vision doc for the most boringly powerful app ever built.*

---

**LOGLINE:** One command rules every app store. A fellowship of small, single-minded
agents carries your app from "it builds on my machine" to "it's live on the App Store
and Google Play" — while you go touch grass.

**THE PROBLEM (Act One):** Shipping a mobile app in 2026 means learning four
different priesthoods. Apple's portal speaks in bundle IDs and provisioning runes.
Google speaks in service accounts and edit transactions. Samsung and Amazon lurk in
the fog with their own dialects. Every store re-asks the same questions — name,
description, screenshots, age rating, pricing — in slightly different costumes, and
punishes you for getting a character count wrong by three.

**THE RING (Act Two):** A single CLI, `ring`. You describe your app ONCE, in one
config file. Then a fellowship of agents walks the release road for you:

- **PREFLIGHT**, the scout — verifies credentials, config, and sanity before
  anyone touches anything. Finds the missing `.p8` at step 0, not step 47.
- **LINT**, the scholar — checks your title, descriptions, and keywords against
  each store's actual character limits. No more "rejected: metadata" emails.
- **ASSETS**, the quartermaster — confirms your icon and screenshots exist and
  are the right shape before a store complains.
- **PUBLISHER**, the envoy — speaks each store's native API: App Store Connect
  on one side, Google Play edits on the other. Dry-run first, always.
- **SCRIBE**, the wordsmith — writes your privacy policy and support page from
  templates, customized to your app, as web-ready HTML. Discloses AdMob honestly,
  because the free version runs ads.
- **PHOTOGRAPHER**, the portraitist — captures your store screenshots at the
  exact required resolutions with headless Chromium, or adopts ones you made.
- **HERALD**, the messenger — carries the docs to GitHub, enables Pages, and
  returns with the live privacy/support URLs your listings demand.
- **REPORTER**, the bard — writes the tale of what happened, so future-you
  knows exactly what past-you shipped.

New store? You don't rewrite the fellowship. You write ONE adapter module that
speaks the store's API, and every agent instantly works with it. Apple and Google
ship in the box. Samsung and Amazon stand ready as documented stubs.

**THE RULES OF THE RING (what it will NOT do):**

1. It never fakes a credential, a screenshot, or a review answer.
2. It never publishes without a dry run first.
3. It never touches a store you didn't name on the command line.
4. Anything Apple or Google force a human to do (ID checks, $99, clicking
   "I agree") stays human — the ring tells you exactly which 5 minutes are yours.

**THE ENDING (Act Three):** `ring --store google release` on a Friday afternoon.
The Publisher commits the edit, the Bard writes the report, and you're at the
roller rink while your app rolls out to 10% of users. The ring is invisible.
That's the point.

*Fin.*
