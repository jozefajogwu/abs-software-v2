from rest_framework import serializers
from .models import UserCategory

class UserCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCategory
        fields = ['id', 'name']
