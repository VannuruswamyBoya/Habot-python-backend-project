import hmac
import hashlib
import json
import requests
import os
from dotenv import load_dotenv

# Load the webhook secret from .env
load_dotenv()
WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', 'webhook_secret_example')

def simulate_successful_payment(order_id):
    print(f"Simulating Razorpay payment for Order ID: {order_id}")
    
    # 1. Construct the payload exactly as Razorpay would send it
    payload_dict = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_1234567890",
                    "order_id": order_id,
                    "status": "captured"
                }
            }
        }
    }
    
    # Razorpay signs the raw JSON string bytes
    payload_body = json.dumps(payload_dict, separators=(',', ':'))
    
    # 2. Generate the HMAC SHA256 signature using your Webhook Secret
    signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 3. Send the HTTP POST request to your local Django server
    url = "http://127.0.0.1:8000/api/v1/payments/webhook/"
    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature
    }
    
    print(f"Sending webhook to {url}...")
    response = requests.post(url, data=payload_body, headers=headers)
    
    print(f"Server responded with Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! The payment was marked as completed and the booking was finalized.")
    else:
        print("Failed to process webhook.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python simulate_webhook.py <razorpay_order_id>")
        print("Example: python simulate_webhook.py order_OqP123456789")
    else:
        simulate_successful_payment(sys.argv[1])
