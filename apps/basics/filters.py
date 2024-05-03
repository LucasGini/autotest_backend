from django_filters import rest_framework as filters
from apps.basics import models


class TestEnvFilter(filters.FilterSet):
    """
    测试环境过滤类
    """
    envName = filters.CharFilter(field_name='env_name', lookup_expr='icontains')
    hosts = filters.CharFilter(field_name='hosts', lookup_expr='icontains')

    class Meta:
        model = models.TestEnv
        fields = ('envName', 'agreement', 'hosts', 'port')
