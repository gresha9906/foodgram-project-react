import csv

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

from recipes.models import (Favourite, Ingredient, IngredientImport,
                            IngredientsInRecipe, Recipe, ShoppingList, Tag)

from .forms import IngredientImportForm


class IngredientsInRecipeInline(admin.TabularInline):
    model = IngredientsInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientsInRecipeInline,)
    list_display = ('name', 'author', 'pub_date')


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    pass


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(IngredientImport)
class IngredientImportAdmin(admin.ModelAdmin):
    list_display = ('csv_file', 'date_add')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(-1, path('csv-upload/', self.upload_csv))
        return urls

    def upload_csv(self, request):
        if request.method == 'POST':
            form = IngredientImportForm(request.POST, request.FILES)
            if form.is_valid():
                form_object = form.save()
                with form_object.csv_file.open('r') as csv_file:
                    rows = csv.reader(csv_file, delimiter=',')
                    for row in rows:
                        Ingredient.objects.update_or_create(
                            name=row[0], measurement_unit=row[1]
                        )
                url = reverse('admin:index')
                messages.success(request, 'Файл успешно импортирован')
                return HttpResponseRedirect(url)
        form = IngredientImportForm()
        return render(request, 'admin/csv_import_page.html', {'form': form})


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
