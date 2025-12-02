from rest_framework import serializers

from core.models.meal import Meal, IngredientEntry


class IngredientEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientEntry
        fields = ('id', 'food_name', 'weight_grams', 'calories', 'protein', 'fat', 'carbs')


class MealSerializer(serializers.ModelSerializer):
    ingredients = IngredientEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Meal
        fields = ('id', 'title', 'date', 'time', 'ingredients', 'total_calories', 'total_protein', 'total_carbs', 'total_fat', 'created_at')
        read_only_fields = ('total_calories', 'total_protein', 'total_carbs', 'total_fat', 'created_at')


class IngredientInputSerializer(serializers.Serializer):
    food_name = serializers.CharField(max_length=200)
    weight_grams = serializers.FloatField(min_value=0)


class MealCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    date = serializers.DateField()
    time = serializers.TimeField()
    ingredients = IngredientInputSerializer(many=True)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('At least one ingredient is required')
        return value

    def validate(self, data):
        # Basic validation already covered by fields.
        return data
