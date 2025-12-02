from rest_framework import serializers
from core.models.workout_log import WorkoutLog


class WorkoutLogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = WorkoutLog
        fields = [
            'id', 'user_id', 'workout_slug', 'calories_burned', 'duration_minutes', 'finished_at', 'created_at', 'updated_at'
        ]

    def validate_calories_burned(self, value):
        if value is None:
            raise serializers.ValidationError('calories_burned is required')
        if value < 0:
            raise serializers.ValidationError('calories_burned must be >= 0')
        return float(value)

    def validate_duration_minutes(self, value):
        if value is None:
            raise serializers.ValidationError('duration_minutes is required')
        if value <= 0:
            raise serializers.ValidationError('duration_minutes must be > 0')
        return float(value)

    def validate_workout_slug(self, value):
        if value and len(value) > 255:
            raise serializers.ValidationError('workout_slug too long')
        return value
