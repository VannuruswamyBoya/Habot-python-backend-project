from django.urls import path
from .views import RazorpayWebhookView, SimulateWebhookView

urlpatterns = [
    path('webhook/', RazorpayWebhookView.as_view(), name='razorpay-webhook'),
    path('simulate-webhook/', SimulateWebhookView.as_view(), name='simulate-webhook'),
]
