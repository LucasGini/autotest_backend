from rest_framework import serializers
from apps.cases.models import TestCase
from apps.cases.models import ProjectsInfo
from apps.cases.models import Precondition
from apps.cases.models import TestSuite
from django.db import transaction
from rest_framework.exceptions import APIException
from common.utils.default_write import default_write
from django.db import connection


class ListProjectsInfoSerializer(serializers.ModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = ProjectsInfo
        fields = '__all__'


class CreateProjectsInfoSerializer(serializers.ModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = ProjectsInfo
        exclude = ('enable_flag', 'created_by', 'updated_by')

    def create(self, validated_data):
        request = self.context.get('request')
        instance = super().create(validated_data)
        default_write(instance, request)
        return instance

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance = super().update(instance, validated_data)
        default_write(instance, request)
        return instance


class CreatePreconditionSerializer(serializers.ModelSerializer):
    """
    创建前置条件序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('enable_flag', 'case', 'created_by', 'updated_by')


class ListPreconditionSerializer(serializers.ModelSerializer):
    """
    查询前置条件序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('case',)


class ListTestCaseSerializer(serializers.ModelSerializer):
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


class CreateTestCaseSerializer(serializers.ModelSerializer):
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
        # 开启事务
        save_id = transaction.savepoint()
        try:
            request = self.context.get('request')
            # 新增测试用例
            instance = super().create(validated_data)
            default_write(instance, request)
            # 新增前置条件
            precondition_data = validated_data.get('precondition', None)
            if precondition_data:
                precondition = Precondition()
                precondition.precondition_case = precondition_data.get('precondition_case', None)
                precondition.case = instance
                default_write(precondition, request)
            transaction.savepoint_commit(save_id)
        except Exception as e:
            # 失败回滚
            transaction.savepoint_rollback(save_id)
            raise APIException(e)

        return instance

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        request = self.context.get('request')
        default_write(instance, request)
        return instance


class ListTestSuiteSerializer(serializers.ModelSerializer):
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


class CreateTestSuiteSerializer(serializers.ModelSerializer):
    """
    测试套件序创建列化器
    """
    class Meta:
        model = TestSuite
        exclude = ('enable_flag', 'created_by', 'updated_by')





