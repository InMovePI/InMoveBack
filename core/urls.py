from django.urls import path

from core.views.meal import (
    SearchFoodView,
    MealListCreateView,
    MealDetailView,
    WeeklySummaryView,
)
from core.views.fooditem import FoodItemViewSet
from core.views.workout_log import LogWorkoutAPIView, ListWorkoutLogsAPIView

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'fooditems', FoodItemViewSet, basename='fooditems')

urlpatterns = [
    path('meals/search-food/', SearchFoodView.as_view(), name='meals-search-food'),
    path('meals/', MealListCreateView.as_view(), name='meals-list-create'),
    path('meals/<int:pk>/', MealDetailView.as_view(), name='meals-detail'),
    path('meals/weekly-summary/', WeeklySummaryView.as_view(), name='meals-weekly-summary'),
    # Workout logs
    path('workouts/log/', LogWorkoutAPIView.as_view(), name='workout-log-create'),
    path('workouts/logs/', ListWorkoutLogsAPIView.as_view(), name='workout-log-list'),
]

# append router urls for fooditems
urlpatterns += router.urls
