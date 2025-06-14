# Generated by Django 4.2.11 on 2024-05-08 08:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0004_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, 'Значение не должно быть меньше 1'
                    ),
                    django.core.validators.MaxValueValidator(
                        32000, 'Значение не должно быть больше 32000'
                    ),
                ],
                verbose_name='Время приготовления в минутах',
            ),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, 'Значение не должно быть меньше 1'
                    ),
                    django.core.validators.MaxValueValidator(
                        32000, 'Значение не должно быть больше 32000'
                    ),
                ],
                verbose_name='Количество',
            ),
        ),
    ]
