from rest_framework import serializers
from apps.cases.models import TestCase
from apps.cases.models import ProjectsInfo
from apps.cases.models import Precondition
from django.db import transaction
from rest_framework.exceptions import APIException


def default_field(obj, request):
    """
    创建时间等默认字段填写
    """
    if request:
        user = request.user
        obj.created_by = user
        obj.updated_by = user
        obj.save()
        return obj
    else:
        return obj


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
        serializer = ListPreconditionSerializer(precondition)
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


class ListPreconditionSerializer(serializers.ModelSerializer):
    """
    前置条件表序列化器
    """

    class Meta:
        model = Precondition
        exclude = ('case',)


class CreatePreconditionSerializer(serializers.ModelSerializer):
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

    precondition = CreatePreconditionSerializer()

    class Meta:
        model = TestCase
        exclude = ('enable_flag', 'created_by', 'updated_by')

    @transaction.atomic()
    def create(self, validated_data):
        """
        新增测试用例
        """
        # 开启事务
        save_id = transaction.savepoint()
        try:
            ModelClass = self.Meta.model
            request = self.context.get('request')
            # 新增测试用例
            instance = ModelClass.objects.create(**validated_data)
            instance = default_field(instance, request)
            precondition_data = validated_data['precondition']
            # 新增前置条件
            if precondition_data:
                precondition = Precondition()
                precondition.precondition_case = precondition_data['precondition_case']
                precondition.case = instance
                precondition = default_field(precondition, request)
                precondition.save()
                transaction.savepoint_commit(save_id)
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            raise APIException(e)
        return instance





