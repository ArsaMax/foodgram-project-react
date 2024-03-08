# Generated by Django 3.2.3 on 2024-03-07 08:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1, message='Время меньше 1 недопустимо.'), django.core.validators.MaxValueValidator(limit_value=32000, message='Время больше 32000 недопустимо.')], verbose_name='Время приготовления, мин.'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Не меньше 1'), django.core.validators.MaxValueValidator(32000, message='Не больше 32000')], verbose_name='Количество'),
        ),
    ]
