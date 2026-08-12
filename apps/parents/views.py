from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Parent
from .serializers import UserRegisterSerializer, ParentSerializer
from drf_spectacular.utils import extend_schema

class UserRegisterView(generics.CreateAPIView):
    """
    Endpoint to create a new API user for authentication.
    Requires an existing authorized user to invoke.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegisterSerializer
    
    @extend_schema(summary="Register a new User", description="Creates a new User account for login.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ParentCreateView(generics.CreateAPIView):
    """
    Endpoint to create a new Parent profile.
    Requires authorization.
    """
    queryset = Parent.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ParentSerializer
    
    @extend_schema(summary="Create a new Parent", description="Creates a new Parent profile.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
