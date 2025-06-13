from django.contrib import admin
from django.utils.html import format_html

from core.constants import INGREDIENT_MIN_AMOUNT
from .models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    """Строчное представление Ингредиента в Рецепте"""

    model = RecipeIngredient
    extra = 1
    min_num = INGREDIENT_MIN_AMOUNT


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка Рецептов"""

    list_display = ('name', 'author')
    list_display_links = ('name', 'author')
    search_fields = ('name', 'author__username')
    search_help_text = 'Поиск по названию рецепта или `username` автора'
    filter_horizontal = ('tags',)
    list_filter = ('tags',)
    readonly_fields = ('in_favorites',)
    inlines = [RecipeIngredientInline]

    fieldsets = (
        (
            None,
            {
                'fields': (
                    'author',
                    ('name', 'cooking_time', 'in_favorites'),
                    'text',
                    'image',
                    'tags',
                )
            },
        ),
    )

    @admin.display(
        description=format_html('<strong>Рецептов в избранных</strong>')
    )
    def in_favorites(self, obj):
        """Количество рецепта в избранном"""
        return FavoriteRecipe.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка Тегов"""

    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка Ингредиентов"""

    list_display = ('name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    search_help_text = 'Поиск по названию ингредиента'


@admin.register(FavoriteRecipe, ShoppingCart)
class AuthorRecipeAdmin(admin.ModelAdmin):
    """Адмика Корзины и Избранных рецептов"""

    list_display = ('id', '__str__')
    list_display_links = ('id', '__str__')
