from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
    def validate(self, data):
        if self.instance is None:  # Chỉ kiểm tra khi tạo mới
            if 'owner' not in data or data['owner'] is None:
                raise serializers.ValidationError({'owner': 'Trường này là bắt buộc.'})
            if 'assignee' not in data or data['assignee'] is None:
                raise serializers.ValidationError({'assignee': 'Trường này là bắt buộc.'})
        return data    
