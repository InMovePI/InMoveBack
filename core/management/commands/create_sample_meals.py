from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models.fooditem import FoodItem
from core.models import User
from core.models.meal import Meal, IngredientEntry


class Command(BaseCommand):
    help = 'Create sample meals (3 meals with 4 ingredients each) and a dev user'

    def handle(self, *args, **options):
        # ensure FoodItem table populated
        if FoodItem.objects.count() == 0:
            self.stdout.write('FoodItem table empty. Run import_taco first.')
            return

        # create dev user
        email = 'devuser@example.com'
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_password('DevPass123!')
            # ensure required fields set
            user.data_nascimento = '2000-01-01'
            user.genero = 'O'
            user.altura_cm = 170
            user.peso_kg = 70
            user.save()

        # pick 12 food items or create small ones
        fis = list(FoodItem.objects.all()[:12])
        if len(fis) < 4:
            # create fallback items
            for name in ('Banana', 'Apple', 'Rice', 'Chicken'):
                fis.append(FoodItem.objects.create(name=name, calories=100, protein=2, carbs=20, fat=1))

        # create 3 meals
        today = timezone.localdate()
        for i in range(3):
            meal = Meal.objects.create(user=user, title=f'Sample Meal {i+1}', date=today, time=timezone.localtime().time())
            total_cal = total_prot = total_carbs = total_fat = 0.0
            # 4 ingredients each
            for j in range(4):
                fi = fis[(i*4 + j) % len(fis)]
                grams = 100.0
                entry = IngredientEntry.objects.create(meal=meal, food_name=fi.name, weight_grams=grams, calories=fi.calories * grams/fi.weight_grams, protein=fi.protein * grams/fi.weight_grams, carbs=fi.carbs * grams/fi.weight_grams, fat=fi.fat * grams/fi.weight_grams)
                total_cal += entry.calories
                total_prot += entry.protein
                total_carbs += entry.carbs
                total_fat += entry.fat

            meal.total_calories = total_cal
            meal.total_protein = total_prot
            meal.total_carbs = total_carbs
            meal.total_fat = total_fat
            meal.save()

        self.stdout.write(self.style.SUCCESS('Sample data created for user devuser@example.com'))