from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from core.serializers.workout_log import WorkoutLogSerializer
from core.models.workout_log import WorkoutLog


class LogWorkoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        # Normalize incoming keys (accept camelCase inputs from frontend)
        if 'caloriesBurned' in data and 'calories_burned' not in data:
            data['calories_burned'] = data.pop('caloriesBurned')
        if 'durationMinutes' in data and 'duration_minutes' not in data:
            data['duration_minutes'] = data.pop('durationMinutes')
        # Infer finishedAt default
        if not data.get('finishedAt') and not data.get('finished_at'):
            data['finished_at'] = timezone.now().isoformat()

        # Accept either workoutId/slug aliases
        if 'workoutId' in data and not data.get('workout_slug'):
            data['workout_slug'] = str(data.pop('workoutId'))
        if 'workoutSlug' in data and not data.get('workout_slug'):
            data['workout_slug'] = data.pop('workoutSlug')

        serializer = WorkoutLogSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create and associate user
        obj = WorkoutLog.objects.create(
            user=user,
            workout_slug=serializer.validated_data.get('workout_slug'),
            calories_burned=serializer.validated_data['calories_burned'],
            duration_minutes=serializer.validated_data['duration_minutes'],
            finished_at=serializer.validated_data['finished_at'],
        )

        out = WorkoutLogSerializer(obj)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ListWorkoutLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        qs = WorkoutLog.objects.filter(user=user).order_by('-finished_at')
        serializer = WorkoutLogSerializer(qs, many=True)
        return Response(serializer.data)
