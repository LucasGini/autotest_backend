from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from apps.cases.models import TestCase
from apps.cases.models import ProjectsInfo
from apps.cases.models import Precondition
from django.db import transaction
from rest_framework.exceptions import APIException
from common.utils.default_write import default_write


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
        raise_errors_on_nested_writes('create', self, validated_data)
        model_class = self.Meta.model
        request = self.context.get('request')
        instance = model_class.objects.create(**validated_data)
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

    precondition = CreatePreconditionSerializer()

    class Meta:
        model = TestCase
        exclude = ('enable_flag', 'created_by', 'updated_by')

    @transaction.atomic()
    def create(self, validated_data):
        """
        创建测试用例
        """
        raise_errors_on_nested_writes('create', self, validated_data)
        model_class = self.Meta.model
        info = model_meta.get_field_info(model_class)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)
        # 开启事务
        save_id = transaction.savepoint()
        try:
            request = self.context.get('request')
            # 新增测试用例
            instance = model_class.objects.create(**validated_data)
            instance = default_write(instance, request)
            # 新增前置条件
            precondition_data = validated_data.get('precondition', None)
            if precondition_data:
                precondition = Precondition()
                precondition.precondition_case = precondition_data.get('precondition_case', None)
                precondition.case = instance
                precondition = default_write(precondition, request)
                precondition.save()
            transaction.savepoint_commit(save_id)
        except Exception as e:
            # 失败回滚
            transaction.savepoint_rollback(save_id)
            raise APIException(e)
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    @transaction.atomic()
    def update(self, instance, validated_data):
        """
        更新测试用例
        """
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        save_id = transaction.savepoint()
        try:
            request = self.context.get('request')
            instance.save()
            # 修改前置条件
            precondition_data = validated_data.get('precondition', None)
            # 如果precondition_data为空，则直接提交事务
            if precondition_data is None:
                transaction.savepoint_commit(save_id)
                return instance
            try:
                precondition = Precondition.objects.get(case=instance.id)
                if precondition_data:
                    if isinstance(precondition_data, dict):
                        for attr, value in precondition_data.items():
                            setattr(precondition, attr, value)
            except Precondition.DoesNotExist:
                precondition = Precondition()
                precondition.precondition_case = precondition_data.get('precondition_case', None)
                precondition.case = instance
                precondition = default_write(precondition, request)
                precondition.save()
            # 保存并提交事务
            precondition.save()
            transaction.savepoint_commit(save_id)
        except Exception as e:
            # 出现异常，回滚事务
            transaction.savepoint_rollback(save_id)
            raise APIException(e)
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance





