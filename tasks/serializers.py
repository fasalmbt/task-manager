from rest_framework import serializers
from .models import Task
from users.models import CustomUser

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate(self, data):
        if data['status'] == Task.Status.COMPLETED:
            if not data.get('completion_report'):
                raise serializers.ValidationError(
                    "Completion report is required when marking task as completed."
                )
            if not data.get('worked_hours'):
                raise serializers.ValidationError(
                    "Worked hours are required when marking task as completed."
                )
        return data

class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('completion_report', 'worked_hours', 'status')
    
    def validate(self, data):
        if data['status'] == Task.Status.COMPLETED:
            if not data.get('completion_report'):
                raise serializers.ValidationError(
                    "Completion report is required when marking task as completed."
                )
            if not data.get('worked_hours'):
                raise serializers.ValidationError(
                    "Worked hours are required when marking task as completed."
                )
        return data