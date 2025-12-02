from django.db import models
import uuid
from django.conf import settings


class WorkoutLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workout_logs')
    workout_slug = models.CharField(max_length=255, blank=True, null=True)
    calories_burned = models.FloatField()
    duration_minutes = models.FloatField()
    finished_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_workoutlog'
        ordering = ['-finished_at']

    def __str__(self):
        return f"{self.user} - {self.workout_slug or 'unknown'} @ {self.finished_at}" 
