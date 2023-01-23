from rest_framework import serializers

import json

class TaskSerializer(serializers.ModelSerializer):
    parameters = serializers.SerializerMethodField()

    def get_parameters(self, obj):
        return json.loads(obj.parameters)

    class Meta:
        from database.models import Task
        model = Task
        fields = ['algorithm', 'target', 'parameters', 'job_id', 'worker_id', 'progress', 'status', 'created_at',
                  'started_at', 'finished_at', 'done', 'failed']