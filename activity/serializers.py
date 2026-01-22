from rest_framework import serializers
from .models import RecentActivity

class RecentActivitySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # shows username instead of user ID

    class Meta:
        model = RecentActivity
        fields = [
            'id',
            'user',
            'app_name',
            'model_name',
            'object_id',
            'action',
            'description',
            'created_at'
        ]
