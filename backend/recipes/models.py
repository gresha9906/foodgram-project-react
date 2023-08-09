from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models

from foodgram.settings import MAX_VALUE, MIN_VALUE
from users.models import CustomUser

LENGTH_MAX = 200


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=LENGTH_MAX)
    measurement_unit = models.CharField(
        'Еденицы измерения', max_length=LENGTH_MAX
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class IngredientImport(models.Model):
    csv_file = models.FileField(upload_to='ingredients/')
    date_add = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_add']
        verbose_name = 'История импорта'
        verbose_name_plural = 'История импорта'

    def __str__(self):
        return f'{self.csv_file} - {self.date_add}'


class Tag(models.Model):
    name = models.CharField('Название', max_length=16)
    color = models.CharField(
        'Цвет',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})', message='Цвет должен быть в формате HEX'
            )
        ],
    )
    slug = models.SlugField('Слаг тега', unique=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название рецепта', max_length=LENGTH_MAX)
    description = models.CharField('Описание рецепта', max_length=LENGTH_MAX)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиент',
    )
    tags = models.ManyToManyField(
        Tag, blank=True, verbose_name='Тег в рецепте', related_name='tag'
    )
    time_to_cook = models.PositiveSmallIntegerField(
        'Время приготовления, в минутах',
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ],
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        null=True,
    )
    image = models.ImageField(blank=True, default=None)
    pub_date = models.DateTimeField(
        'Дата публикации рецепта', auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE),
        ],
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Рецепты не должны повторяться',
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='shopping_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Рецепты в списке покупок уникальны',
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favourite(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='favourite_user'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favourite_recipe',
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Рецепты в избранном не должны повторяться',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в избранное'
