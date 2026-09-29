"""Samsung Galaxy Store adapter — STUB.

The Galaxy Store Seller Portal does not expose a general public release API
comparable to App Store Connect / Play Developer API. To activate this adapter:

1. Enroll as a Samsung Galaxy Store seller: https://seller.samsungapps.com
2. If/when Samsung grants you API access, implement:
   - check_auth(): verify your seller credentials / token
   - publish(ctx): drive their content-registration flow
   - metadata_rules() / asset_rules(): their listing limits
3. Follow the interface in stores/base.py exactly — every agent will
   instantly work with this store once the adapter is real.

Until then, selecting --store samsung prints this guidance and stops.
"""
from .base import StoreAdapter


class SamsungAdapter(StoreAdapter):
    id = "samsung"
    display = "Samsung Galaxy Store"

    def check_auth(self):
        return False, ("STUB: Galaxy Store has no public release API wired up. "
                        "See stores/samsung.py for activation steps.")

    def metadata_rules(self):
        return {}

    def asset_rules(self):
        return {}

    def publish(self, ctx):
        raise SystemExit("STUB: implement SamsungAdapter.publish() per stores/samsung.py.")
