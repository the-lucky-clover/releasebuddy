"""Amazon Appstore adapter — STUB.

Amazon offers a Publishing API for the Appstore, but it requires per-developer
API credentials issued through the Amazon developer portal. To activate:

1. Register at https://developer.amazon.com and request Appstore Publishing API access.
2. Store your client ID / client secret in config.env (AMAZON_CLIENT_ID, etc.).
3. Implement in this module:
   - check_auth(): exchange credentials for a bearer token (Login with Amazon)
   - publish(ctx): create/update app via
     https://developer.amazon.com/docs/appstore-publishing-api/overview.html
   - metadata_rules() / asset_rules(): Amazon's listing limits
4. Follow the interface in stores/base.py exactly.

Until then, selecting --store amazon prints this guidance and stops.
"""
from .base import StoreAdapter


class AmazonAdapter(StoreAdapter):
    id = "amazon"
    display = "Amazon Appstore"

    def check_auth(self):
        return False, ("STUB: Amazon Appstore adapter not activated. "
                        "See stores/amazon.py for activation steps.")

    def metadata_rules(self):
        return {}

    def asset_rules(self):
        return {}

    def publish(self, ctx):
        raise SystemExit("STUB: implement AmazonAdapter.publish() per stores/amazon.py.")
