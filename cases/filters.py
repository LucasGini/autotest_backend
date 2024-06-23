from django_filters import rest_framework as filters

from cases.models import ProjectsInfo, TestCase


class TestProjectFilter(filters.FilterSet):
    """
    测试项目过滤器
    """
    projectName = filters.CharFilter(field_name='project_name', lookup_expr='icontains')

    class Meta:
        model = ProjectsInfo
        fields = ['projectName', 'responsible']


class TestCaseFilter(filters.FilterSet):
    """
    测试用例过滤器
    """

    caseName = filters.CharFilter(field_name='case_name', lookup_expr='icontains')
    path = filters.CharFilter(field_name='path', lookup_expr='icontains')

    class Meta:
        model = TestCase
        fields = ['caseName', 'project', 'priority', 'method', 'path']
