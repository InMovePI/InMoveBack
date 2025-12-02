from rest_framework import serializers

from core.models.fooditem import FoodItem


class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ('id', 'name', 'portion', 'weight_grams', 'calories', 'protein', 'carbs', 'fat', 'country', 'languages')
