import logging
from django.db import transaction
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.payments.razorpay_client import RazorpayClient
from apps.payments.services import handle_webhook_event
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)

class RazorpayWebhookView(APIView):
    """
    Webhook handler for Razorpay events.
    """
    # No auth class because Razorpay sends requests without DRF auth headers
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=dict,
        responses={200: None, 400: None, 500: None},
        summary="Razorpay Webhook Endpoint",
        description="Receives and processes payment.captured and payment.failed events securely from Razorpay."
    )
    def post(self, request):
        webhook_signature = request.headers.get('X-Razorpay-Signature')

        if not webhook_signature:
            logger.warning("Missing Razorpay signature in webhook")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        webhook_body = request.body.decode('utf-8')
        rzp_client = RazorpayClient()
        
        is_valid = rzp_client.verify_webhook_signature(
            webhook_body, 
            webhook_signature, 
            settings.RAZORPAY_WEBHOOK_SECRET
        )

        if not is_valid:
            logger.warning("Invalid Razorpay webhook signature")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event = request.data.get('event')
        payload = request.data.get('payload', {})
        
        try:
            handle_webhook_event(event, payload)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            # Return 200 anyway so Razorpay doesn't keep retrying if it's a persistent error,
            # or 500 if we want retries. We will return 500 for retries on DB errors.
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SimulateWebhookView(APIView):
    """
    Utility endpoint to simulate Razorpay payment.captured webhook.
    """
    permission_classes = []
    
    @extend_schema(
        request={"type": "object", "properties": {"order_id": {"type": "string"}}},
        responses={200: None, 400: None, 500: None},
        summary="Simulate Razorpay Webhook",
        description="Simulates a payment.captured webhook for a given order ID."
    )
    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        payload = {
            "payment": {
                "entity": {
                    "id": "pay_simulated_" + order_id[-10:],
                    "order_id": order_id,
                    "status": "captured"
                }
            }
        }
        
        try:
            handle_webhook_event('payment.captured', payload)
            return Response({"success": True, "message": f"Webhook simulated successfully for {order_id}"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error simulating webhook: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
