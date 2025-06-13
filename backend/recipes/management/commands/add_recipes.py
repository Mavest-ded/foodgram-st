import json
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag


User = get_user_model()


class Command(BaseCommand):
    fake_image = ''
    author = None
    users = User.objects.all()

    def get_author(self):
        return random.choice(self.users)

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/recipes.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not self.get_author():
            self.stdout.write(self.style.ERROR('Doesn\'t exist any user.'))
            return
        try:
            for recipe_data in data:
                self._create_recipe(recipe_data)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

    def _create_recipe(self, recipe_data):
        tags = recipe_data.pop('tags')
        ingredients = recipe_data.pop('ingredients')
        recipe_name = recipe_data['name']
        if Recipe.objects.filter(name=recipe_name).exists():
            self.stdout.write(
                self.style.ERROR(f'Recipe {recipe_name!r} already exists!')
            )
            return

        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=self.get_author(), image=self.fake_image, **recipe_data
            )

            recipe.tags.set(
                Tag.objects.filter(slug__in=tags).values_list('id', flat=True)
            )
            for ingredient in ingredients:
                if not Ingredient.objects.filter(
                    name=ingredient['name']
                ).exists():
                    raise ValueError(
                        f'Ingredient {ingredient["name"]!r} does not exist!'
                    )

                current_ingredient = Ingredient.objects.get(
                    name=ingredient['name']
                )
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=ingredient['amount'],
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully added {recipe_name!r}!')
            )
