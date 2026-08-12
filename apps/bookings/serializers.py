from rest_framework import serializers
from apps.bookings.models import BookingRequest, BookingStatus
from apps.parents.models import Parent
from apps.lsas.models import LSAProfile
from apps.payments.models import Payment

class PaymentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'razorpay_order_id', 'amount', 'currency', 'status']

class BookingCreateRequestSerializer(serializers.Serializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Parent.objects.all(),
        source='parent'
    )
    lsa_id = serializers.PrimaryKeyRelatedField(
        queryset=LSAProfile.objects.all(),
        source='lsa'
    )
    session_start = serializers.DateTimeField()
    session_end = serializers.DateTimeField()

class BookingResponseSerializer(serializers.ModelSerializer):
    payment = PaymentResponseSerializer(read_only=True)
    
    class Meta:
        model = BookingRequest
        fields = [
            'id', 'parent_id', 'lsa_id', 'session_start', 
            'session_end', 'status', 'created_at', 'payment'
        ]
