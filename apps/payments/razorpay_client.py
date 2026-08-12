import razorpay
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class RazorpayClient:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def create_order(self, amount: int, currency: str, receipt: str) -> dict:
        """
        Creates an order on Razorpay.
        amount is in minor units (paise).
        """
        try:
            data = {
                "amount": amount,
                "currency": currency,
                "receipt": receipt
            }
            # The client handles the request and timeout under the hood via requests,
            # but razorpay-python doesn't expose a timeout param nicely. We rely on its default.
            order = self.client.order.create(data=data)
            return order
        except razorpay.errors.RazorpayError as e:
            logger.error(f"Razorpay Order Creation Failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during Razorpay Order Creation: {str(e)}")
            raise e

    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """
        Verifies the payment signature using Razorpay client.
        """
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            logger.warning(f"Invalid Razorpay signature for order {razorpay_order_id}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying signature: {str(e)}")
            return False

    def verify_webhook_signature(self, webhook_body: str, webhook_signature: str, webhook_secret: str) -> bool:
        """
        Verifies webhook signature.
        """
        try:
            self.client.utility.verify_webhook_signature(webhook_body, webhook_signature, webhook_secret)
            return True
        except razorpay.errors.SignatureVerificationError:
            logger.warning("Invalid Razorpay webhook signature")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying webhook signature: {str(e)}")
            return False
