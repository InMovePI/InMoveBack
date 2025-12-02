import logging
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from core.models.meal import Meal, IngredientEntry
from core.serializers.meal import MealSerializer, MealCreateSerializer, IngredientEntrySerializer
from core.services import nutritionix as nutritionix

# OpenAPI / schema helpers
try:
    from drf_spectacular.utils import extend_schema
    from drf_spectacular.types import OpenApiTypes
    from drf_spectacular.utils import OpenApiParameter
    _HAS_SPECTACULAR = True
except Exception:
    extend_schema = lambda *a, **k: (lambda f: f)
    OpenApiTypes = None
    OpenApiParameter = None
    _HAS_SPECTACULAR = False

logger = logging.getLogger(__name__)


class SearchFoodView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(parameters=[
        OpenApiParameter('q', OpenApiTypes.STR, description='Termo de busca', required=True),
        OpenApiParameter('country', OpenApiTypes.STR, description='Filtro de país: BR/BRA/Brazil/Brasil (default BR)'),
        OpenApiParameter('lang', OpenApiTypes.STR, description='Idioma preferido: pt / pt_BR'),
    ])
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response([], status=status.HTTP_200_OK)

        country = request.query_params.get('country')
        lang = request.query_params.get('lang')

        results = nutritionix.search_foods(q, country=country, lang=lang)
        # return list of items already containing id,name,brand,nutrients,countries,languages
        return Response(results, status=status.HTTP_200_OK)


class MealListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MealSerializer

    def get_queryset(self):
        q = Meal.objects.filter(user=self.request.user)
        date = self.request.query_params.get('date')
        if date:
            q = q.filter(date=date)
        return q.order_by('-date', '-time')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MealCreateSerializer
        return MealSerializer

    def create(self, request, *args, **kwargs):
        serializer = MealCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        meal = Meal.objects.create(
            user=request.user,
            title=data['title'],
            date=data['date'],
            time=data['time'],
            total_calories=0,
            total_protein=0,
            total_carbs=0,
            total_fat=0,
        )

        # create ingredient entries and sum totals
        total_cal = total_prot = total_carbs = total_fat = 0.0

        for ing in data['ingredients']:
            name = ing['food_name']
            grams = float(ing['weight_grams'])

            try:
                nutrients = nutritionix.get_nutrients_for_grams(name, grams)
            except Exception as exc:
                logger.warning('Nutritionix failed for %s: %s', name, exc)
                nutrients = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

            entry = IngredientEntry.objects.create(
                meal=meal,
                food_name=name,
                weight_grams=grams,
                calories=nutrients.get('calories', 0.0),
                protein=nutrients.get('protein', 0.0),
                fat=nutrients.get('fat', 0.0),
                carbs=nutrients.get('carbs', 0.0),
            )

            total_cal += entry.calories
            total_prot += entry.protein
            total_carbs += entry.carbs
            total_fat += entry.fat

        # update totals on meal
        meal.total_calories = total_cal
        meal.total_protein = total_prot
        meal.total_carbs = total_carbs
        meal.total_fat = total_fat
        meal.save()

        out = MealSerializer(meal)
        return Response(out.data, status=status.HTTP_201_CREATED)


class MealDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MealSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # queryset already filtered by user, so only owner can delete
        return super().destroy(request, *args, **kwargs)


class WeeklySummaryView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.localdate()
        # monday = weekday 0
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        meals = Meal.objects.filter(user=request.user, date__range=(monday, sunday))

        # initialize dict from monday to sunday
        day_totals = {}
        week_totals = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

        for i in range(7):
            d = monday + timedelta(days=i)
            day_totals[d.isoformat()] = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0}

        for m in meals:
            ds = m.date.isoformat()
            entry = day_totals.get(ds)
            if entry is None:
                continue
            entry['calories'] += float(m.total_calories or 0.0)
            entry['protein'] += float(m.total_protein or 0.0)
            entry['carbs'] += float(m.total_carbs or 0.0)
            entry['fat'] += float(m.total_fat or 0.0)

            week_totals['calories'] += float(m.total_calories or 0.0)
            week_totals['protein'] += float(m.total_protein or 0.0)
            week_totals['carbs'] += float(m.total_carbs or 0.0)
            week_totals['fat'] += float(m.total_fat or 0.0)

        return Response({'days': day_totals, 'week_totals': week_totals}, status=status.HTTP_200_OK)
