from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import BookingCreateRequestSerializer, BookingResponseSerializer
from .services import create_booking
from .exceptions import BookingConflictException, InvalidBookingDataException
from django.utils import timezone
from datetime import timedelta

class BookingCreateView(APIView):
    """
    API view for creating booking requests.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=BookingCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Valid Booking Example',
                summary='A valid future booking',
                description='Creates a booking scheduled for tomorrow with a 2-hour duration.',
                value={
                    "parent_id": 2,
                    "lsa_id": 3,
                    "session_start": (timezone.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "session_end": (timezone.now() + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
                },
                request_only=True
            )
        ],
        responses={201: BookingResponseSerializer, 400: dict, 409: dict},
        summary="Create a new LSA booking",
        description="Creates a booking and a pending payment stub. Validates LSA availability."
    )
    def post(self, request):
        serializer = BookingCreateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "error": {"code": "VALIDATION_ERROR", "details": serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        data = serializer.validated_data
        try:
            booking = create_booking(
                parent=data['parent'],
                lsa=data['lsa'],
                session_start=data['session_start'],
                session_end=data['session_end']
            )
            response_serializer = BookingResponseSerializer(booking)
            return Response(
                {"success": True, "data": response_serializer.data},
                status=status.HTTP_201_CREATED
            )
            
        except InvalidBookingDataException as e:
            return Response(
                {"success": False, "error": {"code": "INVALID_BOOKING", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )
        except BookingConflictException as e:
            return Response(
                {"success": False, "error": {"code": "BOOKING_CONFLICT", "message": str(e)}},
                status=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            # We will handle this more robustly in Phase 9 with global exception handler
            return Response(
                {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
