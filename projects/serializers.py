from rest_framework import serializers
from .models import Project
from users.models import CustomUser
from equipment.models import Equipment
from inventory.models import Inventory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'department', 'role']

class ProjectSerializer(serializers.ModelSerializer):
    assigned_team = UserSerializer(many=True, read_only=True)
    assigned_team_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all(), write_only=True, source='assigned_team'
    )
    equipment = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Equipment.objects.all(), required=False
    )
    inventory = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Inventory.objects.all(), required=False
    )
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), write_only=True, source='owner'
    )

    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'location', 'start_date', 'end_date',
            'budget', 'status', 'owner', 'owner_id',
            'assigned_team', 'assigned_team_ids',
            'equipment', 'inventory', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']