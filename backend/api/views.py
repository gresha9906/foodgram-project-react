from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favourite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingList, Tag)
from users.models import CustomUser, Subscribe
from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .renderers import CSVDataRenderer, TextDataRenderer
from .serializers import (CreateUserSerializer, FavoriteSerializer,
                          IngredientSerializer, PasswordChangeSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingListSerializer, SubscribeSerializer,
                          TagSerializer, UserListSerializer, UserSerializer)


class IngredientViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ['^name']


class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Recipe.objects.prefetch_related(
            'ingredientsinrecipe_set__ingredient', 'tags'
        ).all()

    def get_serializer_class(self):
        if self.action == 'shopping_cart':
            return ShoppingListSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.action in ('create', 'update', 'delete', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST', 'DELETE'])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'DELETE':
            get_object_or_404(
                Favourite, user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(recipe)
        Favourite.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'DELETE':
            get_object_or_404(
                ShoppingList, user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(recipe)
        ShoppingList.objects.create(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
        renderer_classes=[CSVDataRenderer, TextDataRenderer],
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientsInRecipe.objects.filter(
                recipe__shopping_recipe__user=request.user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(
                Ингредиент=F('ingredient__name'),
                Количество=Sum('amount'),
                Единицы_измерения=F('ingredient__measurement_unit'),
            )
        )
        file_name = f'your_shopping_list.{request.accepted_renderer.format}'
        return Response(
            ingredients,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"'
            },
        )


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserListSerializer
        if self.action == 'set_password':
            return PasswordChangeSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return SubscribeSerializer
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET', 'POST', 'DELETE'],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(
            subscribing__user=self.request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(CustomUser, id=kwargs['pk'])
        if request.method == 'DELETE':
            get_object_or_404(
                Subscribe, user=request.user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscribeSerializer(
            author, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(user=request.user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
