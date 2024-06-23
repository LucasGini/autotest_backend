from django_filters import rest_framework as filters
from basics import models


class TestEnvFilter(filters.FilterSet):
    """
    测试环境过滤类
    """
    envName = filters.CharFilter(field_name='env_name', lookup_expr='icontains')
    hosts = filters.CharFilter(field_name='hosts', lookup_expr='icontains')

    class Meta:
        model = models.TestEnv
        fields = ('envName', 'agreement', 'hosts', 'port')


class CategoryConfigFilter(filters.FilterSet):
    """
    类型配置表过滤器
    """
    categoryGroup = filters.CharFilter(field_name='category_group', lookup_expr='exact')
    categoryName = filters.CharFilter(field_name='category_name', lookup_expr='exact')
    categoryCode = filters.CharFilter(field_name='category_code', lookup_expr='exact')
    categoryParentId = filters.CharFilter(field_name='category_parent_id', lookup_expr='exact')

    class Meta:
        model = models.CategoryConfig
        fields = ('categoryGroup', 'categoryName', 'categoryCode', 'categoryParentId')
