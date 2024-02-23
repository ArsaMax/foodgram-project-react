import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзина',
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название', max_length=200, verbose_name='Название')),
                ('measurement_unit', models.CharField(help_text='Укажите единицу измерения ингредиента', max_length=200, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название', max_length=200, unique=True, verbose_name='Название')),
                ('image', models.ImageField(upload_to='recipes/images/')),
                ('cooking_time', models.IntegerField(help_text='Укажите время приготовления (в минутах)', validators=[django.core.validators.MinValueValidator(limit_value=1)], verbose_name='Время приготовления')),
                ('text', models.TextField(help_text='Добавьте описание', verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Укажите название', max_length=200, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(help_text='Укажите слаг', max_length=200, unique=True, verbose_name='Слаг')),
                ('color', models.CharField(max_length=7)),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(limit_value=1)])),
                ('ingredient', models.ForeignKey(help_text='Укажите ингредиент', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(help_text='Укажите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredient', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'Рецепт - Ингредиент',
                'verbose_name_plural': 'Рецепт - Ингредиент',
            },
        ),
    ]
