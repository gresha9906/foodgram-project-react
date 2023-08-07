from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscribe


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'email',
        'username',
        'first_name',
    )
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["email"]}),)
