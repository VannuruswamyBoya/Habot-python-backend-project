from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime
from .models import LSAProfile
from .serializers import LSAProfileSerializer
from .selectors import search_lsas

class LSACreateView(generics.CreateAPIView):
    """
    Endpoint to create a new LSA profile.
    Requires authorization.
    """
    queryset = LSAProfile.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LSAProfileSerializer

    @extend_schema(summary="Create a new LSA", description="Creates a new Learning Support Assistant profile.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })

class LSASearchView(APIView):
    """
    Search available LSAs filtered by skills and time.
    """
    pagination_class = StandardResultsSetPagination
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter('skill', OpenApiTypes.STR, description='Skill to filter by'),
            OpenApiParameter('session_start', OpenApiTypes.DATETIME, description='Session start time (ISO 8601)'),
            OpenApiParameter('session_end', OpenApiTypes.DATETIME, description='Session end time (ISO 8601)'),
            OpenApiParameter('ordering', OpenApiTypes.STR, description='Sort by (name, hourly_rate, created_at, or prefix with - for desc)'),
        ],
        responses={200: LSAProfileSerializer(many=True)},
        summary="Search LSAs",
        description="Search LSAs by skill and availability."
    )
    def get(self, request):
        skill = request.query_params.get('skill')
        session_start_str = request.query_params.get('session_start')
        session_end_str = request.query_params.get('session_end')
        ordering = request.query_params.get('ordering')

        session_start = None
        session_end = None

        if session_start_str and session_end_str:
            try:
                session_start = datetime.fromisoformat(session_start_str.replace('Z', '+00:00'))
                session_end = datetime.fromisoformat(session_end_str.replace('Z', '+00:00'))
            except ValueError:
                return Response(
                    {"success": False, "error": {"code": "INVALID_DATETIME", "message": "Invalid datetime format. Use ISO 8601."}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if session_start >= session_end:
                 return Response(
                    {"success": False, "error": {"code": "INVALID_DATETIME", "message": "session_start must be before session_end."}},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif session_start_str or session_end_str:
            return Response(
                {"success": False, "error": {"code": "MISSING_DATETIME", "message": "Both session_start and session_end must be provided for availability check."}},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = search_lsas(skill=skill, session_start=session_start, session_end=session_end)

        # Ordering whitelist
        if ordering:
            allowed_fields = ['name', '-name', 'hourly_rate', '-hourly_rate', 'created_at', '-created_at']
            if ordering in allowed_fields:
                queryset = queryset.order_by(ordering)
            else:
                 return Response(
                    {"success": False, "error": {"code": "INVALID_ORDERING", "message": f"ordering must be one of {allowed_fields}"}},
                    status=status.HTTP_400_BAD_REQUEST
                )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = LSAProfileSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LSAProfileSerializer(queryset, many=True)
        return Response({"success": True, "data": serializer.data})
