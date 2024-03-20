from rest_framework import serializers
from apps.cases.models import TestCase, TestSuite, ProjectsInfo, Precondition, DependentMethods, TestReport
from django.db import transaction
from rest_framework.exceptions import APIException
from common.utils.default_write import default_write
from common.custom_model_serializer import CustomModelSerializer


class ListProjectsInfoSerializer(CustomModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = ProjectsInfo
        fields = '__all__'


class CreateProjectsInfoSerializer(CustomModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = ProjectsInfo
        exclude = ('enable_flag', 'created_by', 'updated_by')


class CreatePreconditionSerializer(CustomModelSerializer):
    """
    创建前置条件序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('enable_flag', 'case', 'created_by', 'updated_by')


class ListPreconditionSerializer(CustomModelSerializer):
    """
    查询前置条件序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('case',)


class ListTestCaseSerializer(CustomModelSerializer):
    """
    查询测试用例序列化器
    """
    precondition = serializers.SerializerMethodField()
    project = ListProjectsInfoSerializer()

    def get_precondition(self, obj):
        """
        precondition字段方法
        """
        try:
            precondition = Precondition.objects.filter(case_id=obj.id, enable_flag=1)
        except Precondition.DoesNotExist:
            precondition = []
            return precondition
        serializer = ListPreconditionSerializer(precondition, many=True)
        return serializer.data

    class Meta:
        model = TestCase
        fields = '__all__'


class CreateTestCaseSerializer(CustomModelSerializer):
    """
    新增测试用例序列化器
    """

    precondition = CreatePreconditionSerializer(partial=True, required=False)

    class Meta:
        model = TestCase
        exclude = ('enable_flag', 'created_by', 'updated_by')

    @transaction.atomic()
    def create(self, validated_data):
        """
        创建测试用例
        """
        try:
            request = self.context.get('request')
            # 新增测试用例
            instance = super().create(validated_data)
            default_write(instance, request)
            # 新增前置条件
            precondition_data = validated_data.get('precondition', None)
            precondition_case = precondition_data.get('precondition_case', None)
            if precondition_data and precondition_case != '[]':
                precondition = Precondition()
                precondition.precondition_case = precondition_case
                precondition.case = instance
                default_write(precondition, request)
        except Exception as e:
            raise APIException(e)

        return instance


class ListTestSuiteSerializer(CustomModelSerializer):
    """
    测试套件序列表列化器
    """

    case_list = serializers.SerializerMethodField()

    class Meta:
        model = TestSuite
        exclude = ('case',)

    def get_case_list(self, obj):
        queryset = obj.case.filter(enable_flag=1)
        serializer = ListTestCaseSerializer(queryset, many=True)
        return serializer.data


class CreateTestSuiteSerializer(CustomModelSerializer):
    """
    测试套件序创建列化器
    """
    class Meta:
        model = TestSuite
        exclude = ('enable_flag', 'created_by', 'updated_by')


class ListDependentMethodsSerializer(CustomModelSerializer):
    """
    依赖方法列表序列化器
    """

    project_name = serializers.SerializerMethodField()

    class Meta:
        model = DependentMethods
        fields = '__all__'

    def get_project_name(self, obj):
        project_name = obj.project.project_name
        return project_name


class CreateDependentMethodsSerializer(CustomModelSerializer):
    """
    依赖方法创建序列化器
    """

    class Meta:
        model = DependentMethods
        exclude = ('enable_flag', 'created_by', 'updated_by')


class TestReportSerializer(CustomModelSerializer):
    """
    测试报告序列化器
    """
    start_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    created_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = TestReport
        exclude = ('report',)




