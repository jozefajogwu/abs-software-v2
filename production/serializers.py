from rest_framework import serializers
from .models import Operation, Maintenance, Production, DailyProductionRecord

class OperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = '__all__'
        read_only_fields = ['balance']


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'
        read_only_fields = ['balance']


class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = '__all__'
        read_only_fields = ['total']


# --- NEW: Daily Production Serializer ---
class DailyProductionRecordSerializer(serializers.ModelSerializer):
    # These fields are generated automatically by the backend
    efficiency = serializers.ReadOnlyField(source='efficiency_percentage')
    logged_by_name = serializers.ReadOnlyField(source='logged_by.username')

    class Meta:
        model = DailyProductionRecord
        fields = [
            'id', 'date', 'item_name', 'shift', 
            'target_quantity', 'actual_quantity', 
            'defective_quantity', 'efficiency', 
            'notes', 'logged_by', 'logged_by_name', 'created_at'
        ]
        # Prevent these fields from being overwritten by POST/PUT requests
        read_only_fields = ['logged_by', 'created_at']