from django_filters import rest_framework as filters

from apps.cases.models import ProjectsInfo


class TestProjectFilter(filters.FilterSet):
    """
    测试项目过滤器
    """
    projectName = filters.CharFilter(field_name='project_name', lookup_expr='icontains')

    class Meta:
        model = ProjectsInfo
        fields = ['projectName', 'responsible']
