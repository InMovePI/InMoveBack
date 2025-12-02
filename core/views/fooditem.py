from rest_framework import viewsets, permissions

from core.models.fooditem import FoodItem
from core.serializers.fooditem import FoodItemSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class FoodItemViewSet(viewsets.ModelViewSet):
    queryset = FoodItem.objects.all()
    serializer_class = FoodItemSerializer
    permission_classes = [IsAdminOrReadOnly]
