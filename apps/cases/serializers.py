from rest_framework import serializers
from apps.cases.models import TestCase
from apps.cases.models import ProjectsInfo
from apps.cases.models import Precondition


class ListTestCaseSerializer(serializers.ModelSerializer):
    """
    查询测试用例序列化器
    """
    precondition = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    def get_precondition(self, obj):
        """
        precondition字段方法
        """
        try:
            precondition = Precondition.objects.get(case_id=obj.id)
        except Precondition.DoesNotExist:
            precondition = []
            return precondition
        serializer = PreconditionSerializer(precondition)
        return serializer.data

    def get_project(self, obj):
        """
        project字段方法
        """
        try:
            precondition = ProjectsInfo.objects.get(id=obj.project.id)
        except ProjectsInfo.DoesNotExist:
            project = []
            return project
        serializer = ProjectsInfoSerializer(precondition)
        return serializer.data

    class Meta:
        model = TestCase
        fields = '__all__'


class PreconditionSerializer(serializers.ModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('enable_flag', 'case', 'created_by', 'updated_by')


class ProjectsInfoSerializer(serializers.ModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = ProjectsInfo
        fields = '__all__'


class CreateTestCaseSerializer(serializers.ModelSerializer):
    """
    新增测试用例序列化器
    """

    precondition = PreconditionSerializer()

    class Meta:
        model = TestCase
        exclude = ('enable_flag', 'created_by', 'updated_by')




