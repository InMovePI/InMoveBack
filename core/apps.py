from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # On migrations (post_migrate), ensure the TACO data is imported automatically
        # if the FoodItem table is empty. This keeps dev & CI environments populated.
        try:
            from django.db.models.signals import post_migrate
            from django.core.management import call_command
            from django.dispatch import receiver

            from core.models.fooditem import FoodItem

            @receiver(post_migrate)
            def _import_taco(sender, **kwargs):
                try:
                    if FoodItem.objects.count() == 0:
                        # call import_taco to populate by default
                        call_command('import_taco')
                    # After importing taco, if no Meal exists and we're in debug/dev, create sample data
                    try:
                        from core.models.meal import Meal
                        from django.conf import settings
                        if Meal.objects.count() == 0 and getattr(settings, 'DEBUG', False):
                            call_command('create_sample_meals')
                    except Exception:
                        pass
                except Exception:
                    # be silent in environments without DB ready
                    pass
        except Exception:
            pass
