from django.contrib import admin
from apps.users.models import AuthUser


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')

