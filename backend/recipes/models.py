from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_cleanup.cleanup import cleanup_select

from core import abstract_models
from core.constants import (
    COOKING_MIN_TIME,
    INGREDIENT_MAX_LENGTH,
    INGREDIENT_MIN_AMOUNT,
    INGREDIENT_UNIT_MAX_LENGTH,
    MAX_POSITIVE_VALUE,
    RECIPE_MAX_LENGTH_NAME,
    TAG_MAX_LENGTH,
)


class Tag(models.Model):
    """Модель Тегов"""

    name = models.CharField('Название', max_length=TAG_MAX_LENGTH, unique=True)
    slug = models.SlugField('Слаг', max_length=TAG_MAX_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель Ингредиентов"""

    name = models.CharField(
        'Название', max_length=INGREDIENT_MAX_LENGTH, db_index=True
    )
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit',
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


@cleanup_select
class Recipe(abstract_models.AuthorCreatedModel):
    """Модель Рецептов"""

    image = models.ImageField('Картинка', upload_to='recipes/')
    name = models.CharField('Название', max_length=RECIPE_MAX_LENGTH_NAME)
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                COOKING_MIN_TIME,
                f'Значение не должно быть меньше {COOKING_MIN_TIME}',
            ),
            MaxValueValidator(
                MAX_POSITIVE_VALUE,
                f'Значение не должно быть больше {MAX_POSITIVE_VALUE}',
            ),
        ],
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', through='RecipeIngredient'
    )

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель Ингредиентов с количеством для рецепта"""

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                INGREDIENT_MIN_AMOUNT,
                f'Значение не должно быть меньше {INGREDIENT_MIN_AMOUNT}',
            ),
            MaxValueValidator(
                MAX_POSITIVE_VALUE,
                f'Значение не должно быть больше {MAX_POSITIVE_VALUE}',
            ),
        ],
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'], name='unique ingredient'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'

    @classmethod
    def get_shopping_ingredients(cls, user):
        """
        Получение списка ингредиентов для покупки
        :param user:
        :return: [
                    {
                        'name': str,
                        'unit': str,
                        'count': int
                    },
                ]
        """

        return (
            cls.objects.filter(
                models.Q(recipe__in=user.shopping_cart.values('recipe'))
            )
            .values(name=models.F('ingredient__name'))
            .annotate(
                unit=models.F('ingredient__measurement_unit'),
                count=models.Sum('amount'),
            )
            .order_by('ingredient__name')
        )


class FavoriteRecipe(abstract_models.AuthorRecipeModel):
    """Модель Избранных рецептов"""

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'], name='unique recipe favorite'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name!r} в избранном у {self.author.username!r}'


class ShoppingCart(abstract_models.AuthorRecipeModel):
    """Модель Корзины с рецептами"""

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'], name='unique recipe shopping cart'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name!r} в корзине у {self.author.username!r}'
