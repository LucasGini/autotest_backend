from django.contrib import admin
from basics.models import TestEnv, CategoryConfig, SystemMenu


@admin.register(TestEnv)
class TestEnvAdmin(admin.ModelAdmin):
    list_display = ('id', 'env_name', 'agreement', 'hosts', 'port', 'remark')
    search_fields = ('id', 'env_name')
    list_filter = ('env_name',)


@admin.register(CategoryConfig)
class CategoryConfigAdmin(admin.ModelAdmin):
    search_fields = ('id', 'category_name')
    list_filter = ('category_name',)


@admin.register(SystemMenu)
class SystemMenuAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name')
    list_filter = ('name',)

