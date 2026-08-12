from rest_framework import serializers
from .models import LSAProfile

class LSAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LSAProfile
        fields = ['id', 'name', 'email', 'skills', 'hourly_rate', 'is_active']
