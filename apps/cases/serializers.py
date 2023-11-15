from rest_framework import serializers
from apps.cases.models import TestCase


class ListTestCaseSerializer(serializers.ModelSerializer):
    """
    查询测试用例序列化器
    """

    class Meta:
        model = TestCase
        fields = '__all__'


class CreateTestCaseSerializer(serializers.Serializer):
    """
    新增测试用例序列化器
    """
    case_name = serializers.CharField(max_length=128)
