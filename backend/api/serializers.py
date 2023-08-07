from django.contrib.auth.password_validation import validate_password
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from foodgram.settings import MAX_VALUE, MIN_VALUE
from recipes.models import (Favourite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import CustomUser


class IngredientSerializer(serializers.ModelSerializer):
    """GET"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """GET"""

    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.subscribing.exists()
        return False


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError(
                'Current password does not match'
            )
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True, source='ingredientsinrecipe_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(source='time_to_cook')
    text = serializers.CharField(source='description')
    author = UserListSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.favourite_recipe.exists()
        return 'Доступно только авторизованному пользователю'

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.shopping_recipe.exists()
        return 'Доступно только авторизованному пользователю'


class IngredientsInRecipeCreate(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(max_value=MAX_VALUE, min_value=MIN_VALUE)

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(
        source='time_to_cook', max_value=MAX_VALUE, min_value=MIN_VALUE
    )
    text = serializers.CharField(source='description')
    ingredients = IngredientsInRecipeCreate(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    @staticmethod
    def create_ingredients(recipe, ingredients):
        ingredient_liist = []
        for ingredient_data in ingredients:
            ingredient_liist.append(
                IngredientsInRecipe(
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount'],
                    recipe=recipe,
                )
            )
        IngredientsInRecipe.objects.bulk_create(ingredient_liist)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredientsinrecipe_set.all().delete()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class RecipeForSubscribeSerilizer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(source='time_to_cook')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username')

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[: int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeForSubscribeSerilizer(
            recipes, many=True, read_only=True
        ).data

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj.subscribing.exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(source='time_to_cook')
    name = serializers.CharField()
    image = Base64ImageField()

    class Meta:
        model = Favourite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    cooking_time = serializers.IntegerField(source='time_to_cook')
    name = serializers.CharField()
    image = Base64ImageField()

    class Meta:
        model = ShoppingList
        fields = ('id', 'name', 'image', 'cooking_time')
