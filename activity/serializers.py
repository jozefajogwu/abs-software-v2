from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # shows username instead of user ID

    class Meta:
        model = ActivityLog
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
