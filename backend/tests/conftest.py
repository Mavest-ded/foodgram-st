# flake8: noqa: E501
import random
import string

import pytest
from django.contrib.auth.models import AnonymousUser

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


TAGS_COUNT = 3


@pytest.fixture
def password():
    return 'Qwwte7435ge!erty123'


@pytest.fixture
def admin_user(django_user_model, password):
    user_data = {
        'email': 'admin@example.com',
        'username': 'admin',
        'password': password,
        'first_name': 'admin',
        'last_name': 'admin',
        'avatar': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
    }
    return django_user_model.objects.create_superuser(**user_data)


@pytest.fixture
def user(django_user_model, password):
    user_data = {
        'email': 'user@example.com',
        'username': 'default_user',
        'password': password,
        'first_name': 'user',
        'last_name': 'user',
    }
    return django_user_model.objects.create_user(**user_data)


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def create_users(django_user_model, password):
    django_user_model.objects.bulk_create(
        django_user_model(
            **{
                'email': f'user{i}@example.com',
                'username': f'default_user{i}',
                'password': password,
                'first_name': f'user{i}',
                'last_name': f'user{i}',
            }
        )
        for i in range(1, 11)
    )


@pytest.fixture
def user_client(user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.force_login(user)
    return client


@pytest.fixture
def get_token_model():
    from rest_framework.authtoken.models import Token

    return Token


@pytest.fixture
def admin_client_with_token(get_token_model, admin_user):
    from rest_framework.test import APIClient

    client = APIClient()
    token = get_token_model.objects.create(user=admin_user)
    client.force_authenticate(admin_user, token)
    return client


@pytest.fixture
def user_client_with_token(get_token_model, user, user_client):
    token = get_token_model.objects.create(user=user)
    user_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return user_client


@pytest.fixture
def tags():
    return Tag.objects.bulk_create(
        Tag(name=f'tag_{i}', slug=f'tag_{i}') for i in range(TAGS_COUNT)
    )


@pytest.fixture
def ingredients():
    return Ingredient.objects.bulk_create(
        Ingredient(
            name=('A' if i < 3 else 'B')
            + ''.join(random.choice(string.ascii_lowercase) for _ in range(5)),
            measurement_unit=random.choice(['г', 'ч.л.', 'ст.л.']),
        )
        for i in range(10)
    )


@pytest.fixture
def recipes(tags, ingredients, admin_user, user):
    _recipes = Recipe.objects.bulk_create(
        Recipe(
            name=f'Recipe{i}',
            text=f'Text {i}',
            image='',
            cooking_time=1,
            author=admin_user if i % 2 else user,
        )
        for i in range(6)
    )
    for i, recipe in enumerate(Recipe.objects.all(), start=1):
        recipe.tags.set(tags[: random.randint(1, TAGS_COUNT)])
        recipe.save()

        for j in range(1, random.randint(1, 5)):
            if i == j:
                continue
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=j, amount=3
            )
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient_id=i, amount=3
        )
    return _recipes


@pytest.fixture
def favorite_recipe(user, admin_user, recipes):
    FavoriteRecipe.objects.create(author=user, recipe=random.choice(recipes))
    FavoriteRecipe.objects.create(
        author=admin_user, recipe=random.choice(recipes)
    )


@pytest.fixture
def shopping_recipe(user, admin_user, recipes):
    ShoppingCart.objects.create(author=user, recipe=random.choice(recipes))
    ShoppingCart.objects.create(
        author=admin_user, recipe=random.choice(recipes)
    )
